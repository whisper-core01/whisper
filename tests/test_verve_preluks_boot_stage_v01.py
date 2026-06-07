from verve_preluks_boot_stage_v01 import (
    FORBIDDEN_PRELUKS_COMPONENTS,
    REQUIRED_PRELUKS_COMPONENTS,
    FullNixOSMock,
    LuksMock,
    PreLuksStage,
    VerveThreshold,
    WhisperBootMock,
    full_boot_handoff,
    guided_link,
    load_full_nixos,
    luks_attempt_unlock,
    mount_luks_partition,
    pre_luks_boot_summary,
    preluks_contains_forbidden_components,
    preluks_has_required_components,
    preluks_is_not_whisper_core,
    preluks_unlock_requires_no_network,
    start_whisper_after_nixos,
    verve_can_attempt_unlock,
    verve_does_not_access_core,
    verve_zeroize,
)


def test_preluks_stage_contains_required_minimal_components():
    assert guided_link("preluks_stage_contains_required_minimal_components")

    stage = PreLuksStage()

    assert preluks_has_required_components(stage) is True
    assert stage.components == REQUIRED_PRELUKS_COMPONENTS
    assert "minimal_nixos" in stage.components
    assert "minimal_reticulum" in stage.components
    assert "external_rotor" in stage.components
    assert "verve" in stage.components


def test_preluks_stage_contains_no_forbidden_core_components():
    assert guided_link("preluks_stage_contains_no_forbidden_core_components")

    stage = PreLuksStage()

    assert preluks_contains_forbidden_components(stage) is False
    assert stage.components.isdisjoint(FORBIDDEN_PRELUKS_COMPONENTS)


def test_preluks_stage_is_not_whisper_core():
    assert guided_link("preluks_stage_is_not_whisper_core")

    stage = PreLuksStage()

    assert preluks_is_not_whisper_core(stage) is True
    assert stage.can_access_vault is False
    assert stage.can_access_flv is False
    assert stage.can_start_whisper_session is False
    assert stage.can_touch_core_organs is False


def test_preluks_stage_rejects_forbidden_component_presence():
    assert guided_link("preluks_stage_rejects_forbidden_component_presence")

    stage = PreLuksStage()
    stage.components.add("vault_core")

    assert preluks_contains_forbidden_components(stage) is True
    assert preluks_is_not_whisper_core(stage) is False


def test_verve_unlock_does_not_require_network():
    assert guided_link("verve_unlock_does_not_require_network")

    stage = PreLuksStage()
    verve = VerveThreshold()

    assert preluks_unlock_requires_no_network(stage, verve) is True


def test_verve_does_not_access_core():
    assert guided_link("verve_does_not_access_core")

    verve = VerveThreshold()

    assert verve_does_not_access_core(verve) is True
    assert verve.reads_vault is False
    assert verve.reads_flv is False
    assert verve.starts_whisper_directly is False


def test_verve_can_attempt_unlock_with_material():
    assert guided_link("verve_can_attempt_unlock_with_material")

    verve = VerveThreshold()

    assert verve_can_attempt_unlock(verve) is True


def test_verve_zeroizes_unlock_material():
    assert guided_link("verve_zeroizes_unlock_material")

    verve = VerveThreshold()

    verve_zeroize(verve)

    assert verve.has_unlock_material is False
    assert verve.unlock_material_zeroized is True


def test_luks_rejects_wrong_factor_and_zeroizes_verve():
    assert guided_link("luks_rejects_wrong_factor_and_zeroizes_verve")

    luks = LuksMock()
    verve = VerveThreshold()

    decision = luks_attempt_unlock(luks, verve, "wrong-factor")

    assert decision == "unlock_rejected"
    assert luks.locked is True
    assert verve.unlock_material_zeroized is True


def test_luks_accepts_valid_verve_factor():
    assert guided_link("luks_accepts_valid_verve_factor")

    luks = LuksMock()
    verve = VerveThreshold()

    decision = luks_attempt_unlock(luks, verve, "valid-verve-factor")

    assert decision == "unlock_allowed"
    assert luks.locked is False


def test_partition_mount_requires_luks_unlocked():
    assert guided_link("partition_mount_requires_luks_unlocked")

    luks = LuksMock()
    stage = PreLuksStage()

    assert mount_luks_partition(luks, stage) is False
    assert luks.mounted is False

    luks.locked = False

    assert mount_luks_partition(luks, stage) is True
    assert luks.mounted is True
    assert stage.phase == "PARTITION_MOUNTED"


def test_full_nixos_load_requires_partition_mounted():
    assert guided_link("full_nixos_load_requires_partition_mounted")

    luks = LuksMock(locked=False, mounted=False)
    nixos = FullNixOSMock()
    stage = PreLuksStage()

    assert load_full_nixos(luks, nixos, stage) is False

    luks.mounted = True

    assert load_full_nixos(luks, nixos, stage) is True
    assert nixos.loaded is True
    assert nixos.network_stack_available is True
    assert stage.phase == "FULL_NIXOS_LOADED"


def test_whisper_starts_only_after_full_nixos_loaded():
    assert guided_link("whisper_starts_only_after_full_nixos_loaded")

    nixos = FullNixOSMock(loaded=False)
    whisper = WhisperBootMock()
    stage = PreLuksStage()

    assert start_whisper_after_nixos(nixos, whisper, stage) is False
    assert whisper.started is False

    nixos.loaded = True

    assert start_whisper_after_nixos(nixos, whisper, stage) is True
    assert whisper.started is True
    assert whisper.vault_accessible is True
    assert whisper.rotor_available is True
    assert whisper.daemon_started is True
    assert stage.phase == "WHISPER_STARTED"


def test_full_boot_handoff_success_sequence():
    assert guided_link("full_boot_handoff_success_sequence")

    result = full_boot_handoff("valid-verve-factor")

    assert result.unlock_decision == "unlock_allowed"
    assert result.luks_locked is False
    assert result.luks_mounted is True
    assert result.full_nixos_loaded is True
    assert result.whisper_started is True
    assert result.phase == "WHISPER_STARTED"
    assert result.verve_zeroized is True


def test_full_boot_handoff_wrong_factor_does_not_start_whisper():
    assert guided_link("full_boot_handoff_wrong_factor_does_not_start_whisper")

    result = full_boot_handoff("wrong-factor")

    assert result.unlock_decision == "unlock_rejected"
    assert result.luks_locked is True
    assert result.luks_mounted is False
    assert result.full_nixos_loaded is False
    assert result.whisper_started is False
    assert result.phase == "PRE_LUKS"
    assert result.verve_zeroized is True


def test_pre_luks_boot_summary():
    assert guided_link("pre_luks_boot_summary")

    summary = pre_luks_boot_summary()

    assert summary["preluks_has_required_components"] is True
    assert summary["preluks_is_not_whisper_core"] is True
    assert summary["preluks_unlock_requires_no_network"] is True
    assert summary["verve_does_not_access_core"] is True
    assert summary["unlock_decision"] == "unlock_allowed"
    assert summary["final_phase"] == "WHISPER_STARTED"
    assert summary["luks_mounted"] is True
    assert summary["full_nixos_loaded"] is True
    assert summary["whisper_started"] is True
    assert summary["verve_zeroized"] is True

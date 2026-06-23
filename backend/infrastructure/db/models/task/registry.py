_MODELS_LOADED = False


def load_models() -> None:
    global _MODELS_LOADED
    if _MODELS_LOADED:
        return

    # Import ORM models lazily (dependency order: User → Task → Learning).
    import infrastructure.db.models.user.user  # noqa: F401
    import infrastructure.db.models.user.auth_session  # noqa: F401
    import infrastructure.db.models.user.user_role  # noqa: F401
    import infrastructure.db.models.user.user_preferences  # noqa: F401
    import infrastructure.db.models.user.teacher_profile  # noqa: F401
    import infrastructure.db.models.user.teacher_role_request  # noqa: F401
    import infrastructure.db.models.user.teacher_activity  # noqa: F401

    import infrastructure.db.models.task.construction  # noqa: F401
    import infrastructure.db.models.task.collection  # noqa: F401
    import infrastructure.db.models.task.task  # noqa: F401
    import infrastructure.db.models.task.task_version  # noqa: F401
    import infrastructure.db.models.task.task_curriculum_link  # noqa: F401

    import infrastructure.db.models.learning.group  # noqa: F401
    import infrastructure.db.models.learning.invitation_code  # noqa: F401
    import infrastructure.db.models.learning.user_solution  # noqa: F401
    import infrastructure.db.models.learning.submission  # noqa: F401
    import infrastructure.db.models.learning.submission_comment  # noqa: F401
    import infrastructure.db.models.learning.student_learning_profile  # noqa: F401
    import infrastructure.db.models.learning.student_curriculum_progress  # noqa: F401
    import infrastructure.db.models.learning.curriculum_chapter_meta  # noqa: F401

    import infrastructure.db.models.support.support_ticket  # noqa: F401
    import infrastructure.db.models.support.support_ticket_message  # noqa: F401
    import infrastructure.db.models.support.in_app_notification  # noqa: F401

    import infrastructure.db.models.hints.structure_hint  # noqa: F401

    _MODELS_LOADED = True

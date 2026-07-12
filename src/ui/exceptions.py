"""Exception hierarchy for Module 13: NiceGUI Desktop UI.

This module defines all custom exceptions raised within the presentation and user
interface layers of AI Marketing Studio PRO, including view model, state, task,
navigation, dialog, preview, and window manager failures.
"""

class UIError(Exception):
    """Base exception class for all errors originating in the NiceGUI Desktop UI (Module 13)."""
    pass


class UIConfigurationError(UIError):
    """Raised when there is an invalid configuration for the UI application or window setup."""
    pass


class UIInitializationError(UIError):
    """Raised when the UI system, page layouts, or NiceGUI startup parameters fail to initialize."""
    pass


class DesktopWindowError(UIError):
    """Raised when native window creation, geometry restoration, or lifecycle control fails."""
    pass


class NavigationError(UIError):
    """Base exception for navigation-related anomalies."""
    pass


class UnknownRouteError(NavigationError):
    """Raised when requesting navigation to a route or deep link that has not been registered."""
    pass


class ViewCreationError(NavigationError):
    """Raised when page construction or dynamic route factory invocation fails."""
    pass


class ViewModelError(UIError):
    """Base exception for view-model business bindings, state mutations, and command execution."""
    pass


class InvalidUIStateError(ViewModelError):
    """Raised when attempting illegal page or view model state transitions."""
    pass


class UIStateSynchronizationError(ViewModelError):
    """Raised when local UI state fails to synchronize with underlying project metadata or workflow status."""
    pass


class FormValidationError(ViewModelError):
    """Raised when input form fields fail to validate according to presentation rules."""
    pass


class DialogError(UIError):
    """Raised when a modal dialog, confirmation prompt, or user interaction card fails to render or resolve."""
    pass


class NotificationError(UIError):
    """Raised when rendering, showing, or dismissed statuses of a notification toast or banner fails."""
    pass


class TaskManagerError(UIError):
    """Base exception for the UI-safe background asynchronous tasks supervisor."""
    pass


class DuplicateUITaskError(TaskManagerError):
    """Raised when a background task with the same identifier is already executing."""
    pass


class UITaskNotFoundError(TaskManagerError):
    """Raised when trying to query or cancel a task that does not exist in the active registry."""
    pass


class UITaskCancellationError(TaskManagerError):
    """Raised when a task abort or cooperative cancellation request fails to propagate."""
    pass


class PreviewError(UIError):
    """Base exception for asset previews."""
    pass


class UnsupportedPreviewTypeError(PreviewError):
    """Raised when requesting a preview for a mime/media type that is not supported in the UI."""
    pass


class FilePickerError(UIError):
    """Raised when file system dialogs, directory selections, or filter rules encounter errors."""
    pass


class ThemeError(UIError):
    """Raised when applying, switching, or loading styling presets, light/dark configurations, or tokens fails."""
    pass


class ComponentRenderingError(UIError):
    """Raised when a sub-component, header, widget, or layout block crashes during render."""
    pass


class PresentationMappingError(UIError):
    """Raised when mapping domain results, settings, or statistics into visual data objects fails."""
    pass


class WorkflowCommandError(ViewModelError):
    """Raised when a user-initiated workflow command (e.g. run, retry, cancel) fails to propagate or execute."""
    pass


class ProjectCommandError(ViewModelError):
    """Raised when a user-initiated project command (e.g. create, open, save, save-as, close) fails."""
    pass


class UIShutdownError(UIError):
    """Raised when graceful termination, task cancellation, or project locking release on exit fails."""
    pass

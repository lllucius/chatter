"""Analytics exceptions and error handling."""


class AnalyticsError(Exception):
    """Analytics operation error."""

    pass


class ConversationAnalysisError(AnalyticsError):
    """Error during conversation analysis."""

    pass


class PerformanceAnalysisError(AnalyticsError):
    """Error during performance analysis."""

    pass


class TrendAnalysisError(AnalyticsError):
    """Error during trend analysis."""

    pass


class UserBehaviorAnalysisError(AnalyticsError):
    """Error during user behavior analysis."""

    pass
class Planner:

    @staticmethod
    def plan(
        request: str
    ):

        request = request.lower()

        if (
            "report" in request
            or
            "document" in request
        ):

            return (
                "generate_document"
            )

        return (
            "unknown"
        )
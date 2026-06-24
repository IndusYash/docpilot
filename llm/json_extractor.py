import json
import re
import ast


class JSONExtractor:

    @staticmethod
    def extract(
        response: str
    ) -> str:

        response = response.strip()

        response = re.sub(
            r"^```(?:json)?",
            "",
            response,
            flags=re.IGNORECASE
        )

        response = re.sub(
            r"```$",
            "",
            response
        )

        response = response.strip()

        # Valid JSON

        try:

            json.loads(response)

            return response

        except Exception:

            pass

        match = re.search(
            r"\{.*\}",
            response,
            re.DOTALL
        )

        if not match:

            raise ValueError(
                "No JSON-like object found."
            )

        candidate = match.group(0)

        # Proper JSON

        try:

            json.loads(candidate)

            return candidate

        except Exception:

            pass

        # Python dict

        try:

            python_obj = ast.literal_eval(
                candidate
            )

            return json.dumps(
                python_obj
            )

        except Exception:

            pass

        raise ValueError(
            "Could not parse response."
        )
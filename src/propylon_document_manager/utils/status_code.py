class StatusCode:
    @classmethod
    def get_response(cls, status_code):
        return {
            "responseCode": status_code,
            "responseMessage": cls.get_message(status_code),
        }

    @classmethod
    def get_message(cls, status_code):
        return cls.codes.get(status_code)

    invalid_codes = {500: "Invalid Payload"}

    codes = {
        200: "Success",
        202: "Logout Success",
        301: "File Already Exists",
        400: "Request Version does not exist",
        401: "Invalid Refresh Token",
    }

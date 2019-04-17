
class BaseClient:
    def test_base_client(self):
        print("My name is BaseClient!")
        
    def connect(self, **kwargs) -> None:
        raise NotImplementedError("connect() not implemented")

    def get_edgar_path(self, **kwargs) -> list:
        raise NotImplementedError("get_edgar_path() not implemented")

    def save_edgar_path(self, path: list) -> None:
        raise NotImplementedError("save_edgar_path() not implemented")

    def update_edgar_path(self, filter: dict, update: dict) -> None:
        raise NotImplementedError("update_edgar_path() not implemented")

    def update_companie(self, filter: dict, update: dict) -> None:
        raise NotImplementedError("update_companie() not implemented")

    def save_report_positions(self, bulk: list) -> None:
        raise NotImplementedError("save_report_positions() not implemented")

    def save_segments(self, bulk: list) -> None:
        raise NotImplementedError("save_segments() not implemented")

    def get_companies(self, filter: dict, limit: int) -> list:
        raise NotImplementedError("get_companies() not implemented")

    def get_fillings(self, filter: dict, limit: int) -> list:
        raise NotImplementedError("get_fillings() not implemented")
        
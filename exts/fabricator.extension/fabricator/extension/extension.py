import omni.ext
import omni.ui as ui

from .auth_service import AuthService
from .fabricator_service import FabricatorService
from .file_service import FileService

# Functions and vars are available to other extension as usual in python: `example.python_ext.some_public_function(x)`
def some_public_function(x: int):
    print(f"[fabricator.extension] some_public_function was called with {x}")
    return x ** x

# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class FabricatorExtension(omni.ext.IExt):
    DEFAULT_WIDTH = 600
    PER_PAGE = 15

    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        print("[fabricator.extension] fabricator extensiohn startup")

        self._window = ui.Window("Fabricator", width=FabricatorExtension.DEFAULT_WIDTH)

        self.file_service = FileService()
        self.file_service.create_dir()

        self.auth_service = AuthService()
        self.signin_email_input = None
        self.signin_password_input = None
        self._signin_error_msg = None

        self.workspaces = []
        self.current_workspace_idx = 0
        self.workspace_combobox = None

        self.fabricator_service = FabricatorService()
        self.page_search_input = None
        self.page = 1
        self.max_page = 1

        self.render_signin_page()

    def on_shutdown(self):
        print("[fabricator.extension] fabricator extensiohn shutdown")
        self.file_service.remove_dir()

    def current_workspace_id(self):
        return self.workspaces[self.current_workspace_idx]["id"]

    def render_signin_page(self):
        def signin_btn_clicked():
            email = self.signin_email_input.model.get_value_as_string()
            password = self.signin_password_input.model.get_value_as_string()

            try:
                self.auth_service.sign_in(email, password)
                self.fabricator_service.set_access_token(self.auth_service.access_token)
                self.workspaces = self.auth_service.get_workspaces()
                self.render_assets_page()
            except Exception as e:
                print(f"[fabricator.extension] {e}")
                self._signin_error_msg = "Invalid Email or Password"
                self.render_signin_page()

        with self._window.frame:
            with ui.VStack(width=FabricatorExtension.DEFAULT_WIDTH, spacing=10):
                ui.Label("Sign In", alignment=ui.Alignment.CENTER, height=80, style={"font_size": 40})
                ui.Label("with your VMOD account", alignment=ui.Alignment.CENTER_TOP, height=10)
                ui.Label("If you don't have an account, create one at visit vmod.xyz", alignment=ui.Alignment.CENTER_TOP, height=40)
                if self._signin_error_msg is not None:
                    ui.Label(self._signin_error_msg, alignment=ui.Alignment.CENTER, height=10, style={"color": "red"})

                ui.Label("Email:", alignment=ui.Alignment.CENTER_BOTTOM, height=10)
                self.signin_email_input = ui.StringField(placeholder="Email", height=20, style={"margin_width": 40})
                ui.Label("Password:", alignment=ui.Alignment.CENTER_BOTTOM, height=10)
                self.signin_password_input = ui.StringField(password_mode=True, height=20, style={"margin_width": 40})

                ui.Button("Sign In", height=80, style={"margin_width": 100, "margin_height": 20}, clicked_fn=signin_btn_clicked)

    def workspace_selector_component(self):
        self.workspace_combobox = ui.ComboBox(self.current_workspace_idx, *list(map(lambda ws: ws["name"], self.workspaces)), height=10).model

        def workspace_changed(model, item):
            self.current_workspace_idx =  model.get_item_value_model().as_int
            self.page = 1
            self.render_assets_page()

        self.workspace_combobox.add_item_changed_fn(workspace_changed)

    def render_assets_page(self):
        try:
            assets, count = self.fabricator_service.load_assets(self.current_workspace_id(), self.page, FabricatorExtension.PER_PAGE)
            self.max_page = count

            with self._window.frame:
                with ui.VStack(spacing=10, width=FabricatorExtension.DEFAULT_WIDTH, height=400):
                    self.workspace_selector_component()
                    with ui.VGrid(column_width=100, row_height=120, column_count=5, row_count=3):
                        for asset in assets:
                            file_path = self.file_service.save_file(f'{asset["code"]}.usda', asset["asset_url"])
                            self.asset_component(asset, file_path)
                    self.page_search_component()

        except Exception as e:
            print(f"[fabricator.extension] {e}")
            self.render_signin_page()

    def library_page(self):
        with self._window.frame:
            with ui.VStack(spacing=10, width=FabricatorExtension.DEFAULT_WIDTH, height=400):
                self.gnb_component()
                ui.Label("library!!")

    def asset_component(self, asset, file_path):
        def drag_fn(asset):
            asset_name = asset["code"]
            image_url = asset["thumbnail_url"]
            asset_url = asset["asset_url"]

            with ui.VStack():
                ui.Image(image_url, width=100, height=100)

            return file_path

        with ui.VStack():
            asset_name = asset["code"]
            image_url = asset["thumbnail_url"]

            ui.ImageWithProvider(image_url, width=100, height=100, style={"margin_width": 5},
                                 drag_fn=lambda: drag_fn(asset))
            ui.Label(asset_name, alignment=ui.Alignment.CENTER_TOP, width=100, height=20, style={"font_size": 15}, elided_text=True)

    def page_search_component(self):
        curr_page = self.page
        def search_btn_handler():
            m = self.page_search_input.model
            search_page = m.get_value_as_int()
            if search_page == curr_page:
                return
            if search_page < 1 or search_page > self.max_page:
                print("[fabricator.extension] Invalid search range")
                m.set_value(curr_page)
                return
            self.page = search_page
            self.render_assets_page()

        WIDTH = 100
        HEIGHT = 20

        with ui.Placer(offset_x=FabricatorExtension.DEFAULT_WIDTH / 2 - WIDTH / 2):
            with ui.HStack(width=WIDTH, height=HEIGHT):
                self.page_search_input = ui.IntField()
                self.page_search_input.model.set_value(curr_page)
                ui.Label(f" / {self.max_page}")
                ui.Button("search", clicked_fn=search_btn_handler)

    
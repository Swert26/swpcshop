import webview,os
window = webview.create_window(title="Desktop app", url="http://localhost:145")
data_dir = os.path.join(os.getcwd(), "app_storage")
webview.start(private_mode=False, storage_path=data_dir)
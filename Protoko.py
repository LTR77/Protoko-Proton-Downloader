import sys, os, time, threading, subprocess
import tarfile, zipfile, glob

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from qt_material import apply_stylesheet
from pygame import mixer

mixer.init()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        
        # INIT BEGIN

        
        ProtonOptionSelect = [
        "Select Here 🔨",
        "TKG Proton",
        "TKG Proton Experimental",
        "GE Proton",
        "SteamTinkerLaunch",
        "CachyOS Proton",
        "Proton Sarek"
        ]
        
        self.download_dir_selection = os.path.expanduser("~/.steam/steam/compatibilitytools.d/")
        self.default_dir = os.path.expanduser("~/.steam/steam/compatibilitytools.d")
        self.default_steam_path = os.path.expanduser("~/.steam/steam")
        self.flatpak_steam_path = os.path.expanduser("~/.var/app/com.valvesoftware.Steam/.local/share/Steam")
        self.snap_steam_path = os.path.expanduser("~/snap/steam/common/.local/share/Steam")
        
        try:
            print(f"log: Attempting to Load Github Token from local file {"github_token.txt"}")
            if os.path.exists("github_token.txt"):
                token_file = open("github_token.txt", "r")
                saved_token = token_file.read().strip()
                token_file.close()
                os.environ["GITHUB_TOKEN"] = saved_token
                print("log: Loaded github Token from file!")
            else:
                print("log: Couldn't load saved file (maybe it hasent been created yet?)")
                
            print("log: Loading Versions! Please Wait...")
            self.list_version_command_proton_ge = subprocess.run("gh release list --repo GloriousEggroll/proton-ge-custom --limit 30 --json tagName --jq '.[].tagName'", shell=True, text=True, check=True, capture_output=True)
            self.list_version_command_cachyos = subprocess.run("gh release list --repo CachyOS/proton-cachyos --limit 30 --json tagName --jq '.[].tagName'", shell=True, text=True, check=True, capture_output=True)
            self.list_version_command_sarek = subprocess.run("gh release list --repo pythonlover02/Proton-Sarek --limit 30 --json tagName --jq '.[].tagName'", shell=True, text=True, check=True, capture_output=True)
            self.list_version_command_tkg_noexp = subprocess.run("gh run list  --status success --limit 30 -R Frogging-Family/wine-tkg-git -w proton-arch-nopackage.yml --json databaseId -q '.[].databaseId'", shell=True, capture_output=True, check=True, text=True)
            self.list_version_command_tkg_exp = subprocess.run("gh run list  --status success --limit 30 -R Frogging-Family/wine-tkg-git -w proton-valvexbe-arch-nopackage.yml --json databaseId -q '.[].databaseId'", shell=True, capture_output=True, check=True, text=True)
            print("Success!")
        except subprocess.CalledProcessError:
            print(f"log: Failed to Load version list! make sure you have run {"gh auth login"} before trying this")

        print("log: checking for steam installation path")
        if os.path.exists(self.default_steam_path):
            default_dir = os.path.expanduser("~/.steam/steam/compatibilitytools.d/")
            print("log: found native steam installation!")
        elif os.path.exists(self.flatpak_steam_path):
            default_dir = os.path.expanduser("~/.var/app/com.valvesoftware.Steam/.local/share/Steam/compatibilitytools.d")
            print("log: native steam path not found, selecting default flatpak path!")
        elif os.path.exists(self.snap_steam_path):
            default_dir = os.path.expanduser("~/snap/steam/common/.local/share/Steam")
            print("log: native or flatpak steam path not found, selecting default snap path!")

        self.playing_sound = 0
        self.play_sound = "None"
        self.selected = "Select Here 🔨"
        self.destroy_options_on_second_click = False
        self.AuthDestroySecondClick = False
        self.init_list_ver_func = self.list_versions()

        self.setWindowTitle("Protoko")
        self.setFixedSize(680, 400)
        self.playing_sound = 0
        
        Quit = QPushButton(text="Quit")
        Install = QPushButton(text="Install ✅")
        Options = QPushButton(text="Options")
        Sound = QPushButton(text="🔊")
        self.Version_Selection = QComboBox()
        self.Version_Selection.addItems(ProtonOptionSelect)
        self.Version_Selection.setStyleSheet("color: cyan;")
        
        Folder_Selection = QFileDialog(self)
        Folder_Selection.setFileMode(QFileDialog.FileMode.Directory)
        Folder_Selection.setOption(QFileDialog.Option.ShowDirsOnly, True)
        Folder_Selection.directoryEntered.connect(self.Folder)
        
        Quit.clicked.connect(self.QuitFunc)
        Sound.clicked.connect(self.PlaySoundBG)
        Options.clicked.connect(self.OptionsMenu)
        Install.clicked.connect(self.download_proton)
        self.Version_Selection.currentTextChanged.connect(self.Selected_Proton_Version_save)
        self.Version_Selection.currentTextChanged.connect(self.Selected_Proton_Version_save)

        Quit.setMaximumWidth(100)
        Quit.setStyleSheet("color: red;")
        Install.setMaximumWidth(100)
        Install.setStyleSheet("color: green;")
        Options.setMaximumWidth(150)
        Sound.setMaximumWidth(100)
        
        self.centerWidget = QWidget()
        self.setCentralWidget(self.centerWidget)
        
        self.dropChangeVer = QComboBox()
        self.dropChangeVer.addItems(self.init_list_ver_func)
        
        self.dropChangeVer.setStyleSheet("color: cyan;")
        self.dropChangeVer.currentTextChanged.connect(self.Install_Helper)

        self.dropChangeVer.setParent(self.centerWidget)
        self.dropChangeVer.setGeometry(350, 20, 245, 30)
        
        Quit.setParent(self.centerWidget)
        Quit.setGeometry(35, 350, 100, 30)
        
        Install.setParent(self.centerWidget)
        Install.setGeometry(550, 300, 100, 30)
        
        Sound.setParent(self.centerWidget)
        Sound.setGeometry(620, 15, 50, 30)
        
        Options.setParent(self.centerWidget)
        Options.setGeometry(30, 20, 100, 30)
        
        self.Version_Selection.setParent(self.centerWidget)
        self.Version_Selection.setGeometry(150, 20, 180, 30)
        
        
        # INIT END
    
    
    def QuitFunc(self):
        mixer.quit()
        QApplication.instance().quit()
        
    def Folder(self, e):
        self.download_dir_selection = e
        print(f"log: selected folder = {self.download_dir_selection}")
        
    def Selected_Proton_Version_save(self, e):
        self.selected = e
        print(f"log: Selected = {self.selected}")
        ver_list = self.list_versions()
        self.dropChangeVer.clear()
        self.dropChangeVer.addItems(ver_list)
        
    def list_versions(self):
        if self.selected == "GE Proton":
            try:
                output = self.list_version_command_proton_ge.stdout.strip()
                output_list = output.split("\n")
                print("log: Success! Loaded GE Proton's version list.")
                return(output_list)
            except:
                print(f"log: Failed to Load version list! make sure you have run {"gh auth login"} before trying this")
                list_temp = ["Auth Github First!"]
                return(list_temp)
            
        elif self.selected == "Select Here 🔨":
            print("log: skipping selection")
            list_temp = ["Select a version first!"]
            return(list_temp)
            
        elif self.selected == "CachyOS Proton":
            try:
                output = self.list_version_command_cachyos.stdout.strip()
                output_list = output.split("\n")
                return(output_list)
                print("log: Success! Loaded CachyOS Proton's version list.")
            except:
                print(f"log: Failed to Load version list! make sure you have run {"gh auth login"} before trying this")
                list_temp = ["Auth Github First!"]
                return(list_temp)
            
        elif self.selected == "Proton Sarek":
            try:
                output = self.list_version_command_sarek.stdout.strip()
                output_list = output.split("\n")
                return(output_list)
                print("log: Success! Loaded Proton Sarek's version list.")
            except:
                print(f"log: Failed to Load version list! make sure you have run {"gh auth login"} before trying this")
                list_temp = ["Auth Github First!"]
                return(list_temp)

        elif self.selected == "TKG Proton":
            try:
                output = self.list_version_command_tkg_noexp.stdout.strip()
                output_list = output.split("\n")
                return(output_list)
                print("log: Success! Loaded TKG Proton's version list.")
            except subprocess.CalledProcessError:
                print(f"log: Failed to Load version list! make sure you have run {"gh auth login"} before trying this")
                list_temp = ["Auth Github First!"]
                return(list_temp)
                
        elif self.selected == "TKG Proton Experimental":
            try:
                output = self.list_version_command_tkg_exp.stdout.strip()
                output_list = output.split("\n")
                return(output_list)
                print("log: Success! Loaded TKG Proton Experimental's version list.")
            except:
                print(f"log: Failed to Load version list! make sure you have run {"gh auth login"} before trying this")
                list_temp = ["Auth Github First!"]
                return(list_temp)
        elif self.selected == "SteamTinkerLaunch":
            list_temp = ["STL Dosen't support Version Switching!"]
            return(list_temp)
        else:
            print("log: unexpected error! (ignore this!)")
            
            
    # OPTIONS BEGIN
            
            
    def OptionsMenu(self):
        if self.destroy_options_on_second_click == False:
            
            # Download Folder Selection
            self.manual_folder_selection = QPushButton(text="Change Download Folder")
            self.manual_folder_selection.clicked.connect(self.Folder_Selection_Func)
            self.manual_folder_selection.setParent(self.centerWidget)
            self.manual_folder_selection.setGeometry(20, 260, 230, 35)
            self.manual_folder_selection.show()
            
            # Auth Github
            self.AuthGH = QPushButton(text="Auth Github")
            self.AuthGH.clicked.connect(self.AuthGHFunc)
            self.AuthGH.setParent(self.centerWidget)
            self.AuthGH.setGeometry(370, 130, 130, 35)
            self.AuthGH.show()
            
            # Open GH
            self.OpenGH = QPushButton(text="Github 💻")
            self.OpenGH.setParent(self.centerWidget)
            self.OpenGH.setGeometry(260, 170, 130, 35)
            
            self.destroy_options_on_second_click = True
        else:
            self.manual_folder_selection.hide()
            self.AuthGH.hide()
            self.destroy_options_on_second_click = False
            print("log: hidden options menu")
            
    def AuthGHFunc(self):
        if self.AuthDestroySecondClick == False:
            self.PATInput = QComboBox()
            self.PATInput.setEditable(True)
            self.PATInput.setParent(self.centerWidget)
            self.PATInput.setGeometry(390, 190, 200, 35)
            self.PATInput.show()
            self.wdidn = QLabel(text="Enter your Personal Access Token (PAT)")
            self.wdidn.setParent(self.centerWidget)
            self.wdidn.setGeometry(390, 210, 300, 50)
            self.wdidn.show()
            self.AuthDestroySecondClick = True
        else:
            self.wdidn.hide()
            self.PATInput.hide()
            self.AuthDestroySecondClick = False
            
    def CheckBox(self, val):
        self.PATSelection = val
        os.environ["GITHUB_TOKEN"] = self.PATSelection
        print("log: Saving")
        self.wdidn.setText("Saving")
        self.wdidn.setStyleSheet("color: green;")
        token_file = open("github_token.txt", "w")
        token_file.write(self.PATSelection)
        token_file.close()
        try:
            if os.path.exists("github_token.txt"):
                token_file = open("github_token.txt", "r")
                saved_token = token_file.read().strip()
                token_file.close()
                os.environ["GITHUB_TOKEN"] = saved_token
                print("log: Loaded github Token from file!")
                self.wdidn.setText("Loaded!")
                self.wdidn.setStyleSheet("color: green;")
                self.PATInput.hide()
                self.wdidn.hide()
            else:
                self.Error = QLabel(text="Failed to Load Save File")
                self.Error.setStyleSheet("color: red;")
                self.Error.show()
                print("log: Couldn't load saved file (maybe it hasent been created yet?)")
        except:
            print("log: Emotional Damage")
        self.wdidn.hide()
        self.PATInput.hide()
        
    def KeyCheckToken(self, e):
        if e.key() == Qt.Key.Key_Enter or e.key() == Qt.Key.Key_Return:
            self.PATInput.currentText(self.CheckBox())
            return True
        return False

    def Folder_Selection_Func(self):
        self.download_dir_selection = QFileDialog.getExistingDirectory(self, "Select Download Dir", self.default_dir)
        print(f"log: dir = {self.download_dir_selection}")
            
            
    # OPTIONS END
    
    
    # HELPERS BEGIN
    
    
    def Install_Helper(self, svp):
        self.selected_version_proton = svp
        
        
    # HELPERS END
    
    
    def download_proton(self):
        if self.selected == "GE Proton":
            try:
                print("log: selected GE Proton, continuuing")
                download_dir = self.download_dir_selection
                download_path = os.path.join(download_dir, "GE-Proton.tar.gz")
                print("log: Downloading...")
                subprocess.run(f"wget -q https://github.com/GloriousEggroll/proton-ge-custom/releases/download/{self.selected_version_proton}/{self.selected_version_proton}.tar.gz -O {download_path}", shell=True, check=True)
                print("log: Extracting...")
                tar = tarfile.open(f"{download_path}", "r:gz")
                tar.extractall(path=download_dir)
                tar.close()
                subprocess.run(f"rm {download_path}", shell=True)
                time.sleep(2)
                print("log: Completed!")
                time.sleep(4)
            except subprocess.CalledProcessError:
                print("log: Error!", "Check Internet Connection or Curl/WGet/Tar Installation!")
                time.sleep(2)
            except tarfile.TarError:
                print("log: Error!, Bad Tar File!")
                time.sleep(2)
        if self.selected == "Proton Sarek":
            try:
                print("log: selected Proton Sarek, continuuing")
                download_dir = self.download_dir_selection
                download_path = os.path.join(download_dir, "Proton-Sarek.tar.gz")
                print("log: Downloading...")
                subprocess.run(f"wget https://github.com/pythonlover02/Proton-Sarek/releases/download/{self.selected_version_proton}/{self.selected_version_proton}.tar.gz -O {download_path}", shell=True, check=True)
                print("log: Extracting...")    
                tar = tarfile.open(f"{download_path}", "r:gz")
                tar.extractall(path=download_dir)
                tar.close() 
                subprocess.run(f"rm {download_path}", shell=True)
                time.sleep(2)
                print("log: Completed!")
                time.sleep(4)
            except subprocess.CalledProcessError:
                print("log: Error!", "Check Internet Connection or Curl/WGet/Tar Installation!")
                time.sleep(2)
        if self.selected == "CachyOS Proton":
            try:
                print("log: selected CachyOS Proton, continuuing")
                download_dir = self.download_dir_selection
                download_path = os.path.join(download_dir, f"proton-{self.selected_version_proton}-x86_64.tar.xz")
                print("log: Downloading...")
                subprocess.run(f"wget https://github.com/CachyOS/proton-cachyos/releases/download/{self.selected_version_proton}/proton-{self.selected_version_proton}-x86_64.tar.xz -O {download_path}", shell=True, check=True)
                print("log: Extracting...")
                tar = tarfile.open(f"{download_path}", "r")
                tar.extractall(path=download_dir)
                tar.close()
                time.sleep(2)
                print("log: Completed!")
                time.sleep(4)
            except subprocess.CalledProcessError:
                print("log: Error!", "Check Internet Connection or Curl/WGet/Tar Installation!")
                time.sleep(2)
        if self.selected == "SteamTinkerLaunch":
            try:
                print("log: selected STL, continuuing")
                download_dir = self.download_dir_selection
                download_path = os.path.join(download_dir, "master.zip")
                print("log: Downloading...")
                subprocess.run(f"wget -P {download_dir} https://github.com/sonic2kk/steamtinkerlaunch/archive/refs/heads/master.zip", shell=True, check=True)
                if download_dir == self.default_dir:
                    print("log: Extracting...")
                    zip = zipfile.ZipFile(download_path, "r")
                    zip.extractall(path=download_dir)
                    zip.close()
                    subprocess.run(f"chmod +x {download_dir}steamtinkerlaunch-master/steamtinkerlaunch && {download_dir}steamtinkerlaunch-master/steamtinkerlaunch compat add", shell=True)
                    subprocess.run(f"rm {download_path} && rm -rf {download_dir}/steamtinkerlaunch-master", shell=True)
                time.sleep(2)
                # SuccessLabel = ttk.Label(root, text="Installed Successfully!", style="GreenFartation.TLabel")
                print("log: Completed!")
                time.sleep(4)
            except subprocess.CalledProcessError:
                print("log: Error!", "Check Internet Connection or Curl/WGet/Tar Installation!")
                time.sleep(2)
            except zipfile.BadZipFile:
                print("log: Error!, Bad Zip File!")
                time.sleep(2)
        if self.selected == "TKG Proton":
            try:
                print("log: selected TKG Proton, continuuing")
                print("log: running download script!")
                subprocess.run(f"gh run download -R Frogging-Family/wine-tkg-git {self.selected_version_proton} -D {self.download_dir_selection}", shell=True)
                download_dir = self.download_dir_selection
                download_path = os.path.join(download_dir, "proton-tkg-build/*.tar")
                files = glob.glob(download_path)
                print("log: Extracting...")
                tar = tarfile.open(files[0], "r")
                tar.extractall(path=download_dir)
                tar.close()
                subprocess.run(f"rm -rf {download_dir}/proton-tkg-build", shell=True)
                time.sleep(2)
                print("log: Completed!")
                time.sleep(4)
            except subprocess.CalledProcessError:
                print("log: Error!", "Check Internet Connection or Curl/WGet/Tar Installation!")
                time.sleep(2)
        if self.selected == "TKG Proton Experimental":
            try:
                print("log: selected TKG Proton Experimental, continuuing")
                #progress.place(x=200, y=370)
                print("log: running download script!")
                subprocess.run(f"gh run download -R Frogging-Family/wine-tkg-git {self.selected_version_proton} -D {self.download_dir_selection}", shell=True)
                download_dir = self.download_dir_selection
                download_path = os.path.join(download_dir, "proton-tkg-build/*.tar")
                files = glob.glob(download_path)
                print("log: Extracting...")
                tar = tarfile.open(files[0], "r")
                tar.extractall(path=download_dir)
                tar.close()
                subprocess.run(f"rm -rf {download_dir}/proton-tkg-build", shell=True)
                time.sleep(2)
                print("log: Completed!")
                time.sleep(4)
            except subprocess.CalledProcessError:
                print("log: Error!", "Check Internet Connection or Curl/WGet/Tar Installation!")
                time.sleep(2)
        
    def PlaySound(self):
        if self.playing_sound == 0:
            mixer.unpause()
            sound1 = mixer.Sound("resources/dbb.mp3")
            self.play_sound = sound1.play()
            self.playing_sound = 1
        elif self.playing_sound == 1:
            if self.play_sound:
                self.play_sound.stop()
            sound2 = mixer.Sound("resources/jj.mp3")
            self.play_sound = sound2.play()
            self.playing_sound = 2
        elif self.playing_sound == 2:
            self.play_sound.stop()
            mixer.pause()
            self.playing_sound = 0
            
        # the _ dosent actually mean anything its just a trash variable
    def PlaySoundBG(self, _=None):
        thread_sound = threading.Thread(target=self.PlaySound)
        thread_sound.start()
        
app = QApplication(sys.argv)
apply_stylesheet(app, theme='dark_cyan.xml')
window = MainWindow()
window.show()

app.exec()


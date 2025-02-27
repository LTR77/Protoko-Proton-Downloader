import tkinter
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog
import webbrowser
import pygame
import time
import threading
import sv_ttk
import tarfile
import zipfile
import subprocess
import os

pygame.mixer.init()
root = Tk()
print("log: Loading")
sv_ttk.set_theme("dark")
root.title("Protoko")
root.geometry('680x400')

progress = ttk.Progressbar(root, orient=HORIZONTAL, length=200, mode='determinate')
lbltellwarning = ttk.Label(root, text="You must Authenticate Github to use TKG Proton!")
lbltellwarning.place(x=140, y=60)

download_dir_selection = os.path.expanduser("~/.steam/steam/compatibilitytools.d/")
default_dir = os.path.expanduser("~/.steam/steam/compatibilitytools.d")
default_steam_path = os.path.expanduser("~/.steam/steam")

# check to see if you have a flatpak steam installation
if os.path.exists(default_steam_path):
    default_dir = os.path.expanduser("~/.steam/steam/compatibilitytools.d/")
    print("log: found native steam installation!")
else:
    default_dir = os.path.expanduser("~/.var/app/com.valvesoftware.Steam/data/Steam/compatibilitytools.d")
    print("log: native steam path not found, selecting default flatpak path!")

# None's and False's and Null's
destroy_text_on_second_click = False
playing_sound = 0
delallbtn_command = None
openGithubbtn = None
changeDownloadLocation = None
authGithubbtn = None
output_list = []

ProtonOptionSelect = [
    "TKG Proton",
    "TKG Proton",
    "TKG Proton Experimental",
    "GE Proton",
    "SteamTinkerLaunch",
    "CachyOS Proton",
    "Proton Sarek"
]

def update_version_menu(*args):
    new_versions = list_versions()
    change_version.set(new_versions[0])
    menu = dropChangeVer["menu"]
    menu.delete(0, "end")
    for version in new_versions:
        menu.add_command(label=version, command=lambda v=version: change_version.set(v))

clicked = StringVar()
clicked.set("Select Here!")
dropProtonSelect = ttk.OptionMenu(root , clicked , *ProtonOptionSelect)
dropProtonSelect.place(x=130, y=20)
clicked.trace("w", update_version_menu)

def encapsulate_the_dangerous_variable():
    global delallbtn_command, default_dir
    pathOfFiles = default_dir
    delallbtn_command = subprocess.run(f"rm -rf {pathOfFiles}/*", shell=True)

def Authenticate_Github():
    authentication = subprocess.Popen("gh auth login --hostname github.com --git-protocol https --web", shell=True, stdout=subprocess.PIPE)
    messagebox.showinfo("Auth", "Check Console!")

def Authenticate_Github_Background():
    thread_auth = threading.Thread(target=Authenticate_Github)
    thread_auth.start()

def openDescription():
    selected = clicked.get()
    if selected == "GE Proton":
        messagebox.showinfo("Description", "Compatibility tool for Steam Play based on Wine and additional components")
    elif selected == "SteamTinkerLaunch":
        messagebox.showinfo("Description", "Linux wrapper tool for use with the Steam client for custom launch options and 3rd party programs")
    elif selected == "TKG Proton":
        messagebox.showinfo("Description", "The wine-tkg build systems, to create custom Wine and Proton builds, Based on Latest Wine")
    elif selected == "TKG Proton Experimental":
        messagebox.showinfo("Description", "The wine-tkg build systems, to create custom Wine and Proton builds, Based on Latest Proton Experimental")
    else:
        messagebox.showerror("Not Found!")

# stdout prints the result that would normally show in the console
def options():
    global destroy_text_on_second_click, entry_box, lbltelldelete, lblshowdirs, delallbtn_command, deleteallbtn, openGithubbtn, changeDownloadLocation, download_dir_selection, showDownloadLocation, authGithubbtn
    pathOfFiles = default_dir
    if destroy_text_on_second_click == False:
        btnReadDescription.place_forget()
        changeDownloadLocation = ttk.Button(root, text="Change Download Location", command=manualFolderSelection)
        changeDownloadLocation.place(x=370, y=210)
        showDownloadLocation = ttk.Label(root, text=download_dir_selection)
        showDownloadLocation.place(x=320, y=250)
        openGithubbtn = ttk.Button(root, text="Github 💻", command=openGH)
        openGithubbtn.place(x=370, y=170)
        authGithubbtn = ttk.Button(root, text="Auth Github", command=Authenticate_Github_Background)
        authGithubbtn.place(x=500, y=170)
        deleteallbtn = ttk.Button(root, text="Delete all ❌", command=encapsulate_the_dangerous_variable)
        deleteallbtn.place(x=370, y=130)
        entry_box = ttk.Entry(root, width=15)
        entry_box.bind("<Return>", check_text)
        entry_box.place(x=210, y=90)
        lbltelldelete = Label(root, text = "< Type what you want to delete here")
        lbltelldelete.place(x=370, y=100)
        result = subprocess.run("ls ~/.steam/steam/compatibilitytools.d", shell=True, text=True, capture_output=True)
        lblshowdirs = Label(root, text=result.stdout, wraplength=180, justify="left")
        lblshowdirs.place(x=20, y=100)
        destroy_text_on_second_click = True
    else:
        btnReadDescription.place(x=530, y=250)
        authGithubbtn.destroy()
        openGithubbtn.destroy()
        entry_box.destroy()
        lbltelldelete.destroy()
        lblshowdirs.destroy()
        deleteallbtn.destroy()
        changeDownloadLocation.destroy()
        showDownloadLocation.destroy()
        print("log: removed (second click detected)")
        destroy_text_on_second_click = False

def check_text(event):
    global entry_box
    pathOfFiles = default_dir
    user_input = entry_box.get().strip()
    try:
        files_in_dir = os.listdir(pathOfFiles)
        if user_input in files_in_dir:
            full_path = os.path.join(pathOfFiles, user_input)
            subprocess.run(f"rm -rf {full_path}", check=True, shell=True)
            lbltelldelete.config(text="Deleted!")
        else:
            lbltelldelete.config(text="File Not Found! You have probably made a typo!")
    except FileNotFoundError:
            lbltelldelete.config(text="Error: File or Directory not found!")
    except subprocess.CalledProcessError:
            lbltelldelete.config(text="Error: Failed to delete the folder!")

def playSound():
    global playing_sound, play_sound
    if playing_sound == 0:
        pygame.mixer.unpause()
        sound1 = pygame.mixer.Sound("resources/dbb.mp3")
        play_sound = sound1.play()
        playing_sound = 1
    elif playing_sound == 1:
        if play_sound:
            play_sound.stop()
        sound2 = pygame.mixer.Sound("resources/jj.mp3")
        play_sound = sound2.play()
        playing_sound = 2
    elif playing_sound == 2:
        play_sound.stop()
        pygame.mixer.pause()
        playing_sound = 0

def playSound_background():
    thread_sound = threading.Thread(target=playSound)
    thread_sound.start()

def full_quit():
    global play_sound
    root.destroy()
    pygame.mixer.quit()

def openGH():
    selected_page = clicked.get()
    if selected_page == "GE Proton":
        try:
            GE_Proton_Github = webbrowser.open("https://github.com/GloriousEggroll/proton-ge-custom")
        except:
            print("log: Network Error!")
    elif selected_page == "SteamTinkerLaunch":
        try:
            STL_Github = webbrowser.open("https://github.com/sonic2kk/steamtinkerlaunch")
        except:
            print("log: Network Error!")
    elif selected_page == "TKG Proton":
        try:
            TKG_Proton_Github = webbrowser.open("https://github.com/Frogging-Family/wine-tkg-git")
        except:
            print("log: Network Error!")
    elif selected_page == "TKG Proton Experimental":
        try:
            TKG_Proton_Github = webbrowser.open("https://github.com/Frogging-Family/wine-tkg-git")
        except:
            print("log: Network Error!")
    else:
        print("log: Unknown URL!")

def manualFolderSelection():
    global download_dir_selection, default_dir
    default_dir_for_selection = default_dir
    download_dir_selection = filedialog.askdirectory(initialdir=default_dir_for_selection, title="Select Download Folder")

def list_versions():
    selected = clicked.get()
    if selected == "GE Proton":
        list_version_command = subprocess.run("gh release list --repo GloriousEggroll/proton-ge-custom --limit 35 --json tagName --jq '.[].tagName'", shell=True, text=True, check=True, capture_output=True)
        output = list_version_command.stdout.strip()
        output_list = output.split("\n")
        output_list.insert(0, "GE-Proton9-25")
        return(output_list)
    elif selected == "CachyOS Proton":
        list_version_command = subprocess.run("gh release list --repo CachyOS/proton-cachyos --limit 35 --json tagName --jq '.[].tagName'", shell=True, text=True, check=True, capture_output=True)
        output = list_version_command.stdout.strip()
        output_list = output.split("\n")
        return(output_list)
    elif selected == "Proton Sarek":
        list_version_command = subprocess.run("gh release list --repo pythonlover02/Proton-Sarek --limit 35 --json tagName --jq '.[].tagName'", shell=True, text=True, check=True, capture_output=True)
        output = list_version_command.stdout.strip()
        output_list = output.split("\n")
        return(output_list)
    elif selected == "TKG Proton":
        list_temp = ["Not Implemented!"]
        return(list_temp)
    elif selected == "TKG Proton Experimental":
        list_temp = ["Not Implemented!"]
        return(list_temp)
    else:
        print("log: unexpected error!")

init_list_ver_func = list_versions()
change_version = StringVar()
change_version.set("Change Version 👀")
dropChangeVer = ttk.OptionMenu(root , change_version , *init_list_ver_func)
dropChangeVer.place(x=350, y=20)

def download_proton():
    global style, progress
    selected = clicked.get()
    selected_version_proton = change_version.get()
    if selected == "GE Proton":
        try:
            #progress.place(x=200, y=370)
            print("log: selected GE Proton, continuuing")
            #progress["value"] = 10
            #progress["value"] = 20
            download_dir = download_dir_selection
            download_path = os.path.join(download_dir, "GE-Proton.tar.gz")
            #progress["value"] = 30
            print("log: Downloading...")
            #progress["value"] = 40
            subprocess.run(f"wget -q https://github.com/GloriousEggroll/proton-ge-custom/releases/download/{selected_version_proton}/{selected_version_proton}.tar.gz -P {download_dir} -O GE-Proton.tar.gz", shell=True, check=True)
            #progress["value"] = 60
            print("log: Extracting...")
            tar = tarfile.open("GE-Proton.tar.gz", "r:gz")
            tar.extractall(path=download_dir)
            tar.close()
            #progress["value"] = 80
            subprocess.run(f"rm {download_path}", shell=True)
            #progress["value"] = 100
            time.sleep(2)
            SuccessLabel = ttk.Label(root, text="Installed Successfully!", style="GreenFartation.TLabel")
            SuccessLabel.place(x=530, y=370)
            print("log: Completed!")
            #progress.destroy()
        except subprocess.CalledProcessError:
            #progress["value"] = 0
            messagebox.showerror("Error!", "Check Internet Connection or Curl/WGet Installation!")
            time.sleep(2)
            #progress.destroy()
        except tarfile.TarError:
            progress["value"] = 0
            messagebox.showerror("Error!", "Bad Tar File!")
            time.sleep(2)
            #progress.place_forget()
    if selected == "Proton Sarek":
        try:
            print("log: selected Proton Sarek, continuuing")
            print("log: selected CachyOS Proton, continuuing")
            download_dir = download_dir_selection
            download_path = os.path.join(download_dir, "Proton-Sarek.tar.gz")
            print("log: Downloading...")
            subprocess.run(f"wget https://github.com/pythonlover02/Proton-Sarek/releases/download/{selected_version_proton}/{selected_version_proton}.tar.gz -O {download_path}", shell=True, check=True)
            print("log: Extracting...")
            subprocess.run(f"tar -xf {download_path} -C {download_dir}", shell=True)
            subprocess.run(f"rm {download_path}", shell=True)
            time.sleep(2)
            SuccessLabel = ttk.Label(root, text="Installed Successfully!", style="GreenFartation.TLabel")
            SuccessLabel.place(x=530, y=370)
            print("log: Completed!")
        except subprocess.CalledProcessError:
            messagebox.showerror("Error!", "Check Internet Connection or Curl/WGet/Tar Installation!")
            time.sleep(2)
    if selected == "CachyOS Proton":
        try:
            print("log: selected CachyOS Proton, continuuing")
            download_dir = download_dir_selection
            download_path = os.path.join(download_dir, "CachyOS-Proton.tar.xz")
            print("log: Downloading...")
            subprocess.run(f"wget https://github.com/CachyOS/proton-cachyos/releases/download/{selected_version_proton}/proton-{selected_version_proton}-x86_64.tar.xz -O {download_path}", shell=True, check=True)
            print("log: Extracting...")
            subprocess.run(f"tar -xf {download_path} -C {download_dir}", shell=True)
            subprocess.run(f"rm {download_path}", shell=True)
            time.sleep(2)
            SuccessLabel = ttk.Label(root, text="Installed Successfully!", style="GreenFartation.TLabel")
            SuccessLabel.place(x=530, y=370)
            print("log: Completed!")
        except subprocess.CalledProcessError:
            messagebox.showerror("Error!", "Check Internet Connection or Curl/WGet/Tar Installation!")
            time.sleep(2)
    if selected == "SteamTinkerLaunch":
        try:
            print("log: selected STL, continuuing")
            #progress.place(x=200, y=370)
            #progress["value"] = 30
            download_dir = download_dir_selection
            download_path = os.path.join(download_dir, "master.zip")
            print("log: Downloading...")
            subprocess.run(f"wget -P {download_dir} https://github.com/sonic2kk/steamtinkerlaunch/archive/refs/heads/master.zip", shell=True, check=True)
            #progress["value"] = 60
            if download_dir == default_dir:
                print("log: Extracting...")
                zip = zipfile.ZipFile(download_path, "r")
                zip.extractall(path=download_dir)
                zip.close()
                #progress["value"] = 80
                subprocess.run(f"chmod +x {download_dir}steamtinkerlaunch-master/steamtinkerlaunch && {download_dir}steamtinkerlaunch-master/steamtinkerlaunch compat add", shell=True)
                subprocess.run(f"rm {download_path} && rm -rf {download_dir}/steamtinkerlaunch-master", shell=True)
            #progress["value"] = 100
            time.sleep(2)
            SuccessLabel = ttk.Label(root, text="Installed Successfully!", style="GreenFartation.TLabel")
            SuccessLabel.place(x=530, y=370)
            print("log: Completed!")
            #progress.place_forget()
        except subprocess.CalledProcessError:
            #progress["value"] = 0
            messagebox.showerror("Error!", "Check Internet Connection or Curl/WGet Installation!")
            time.sleep(2)
            #progress.place_forget()
        except zipfile.BadZipFile:
            #progress["value"] = 0
            messagebox.showerror("Error!", "Bad Zip File!")
            time.sleep(2)
            #progress.place_forget()
    if selected == "TKG Proton":
        try:
            print("log: selected TKG Proton, continuuing")
            #progress = ttk.Progressbar(root, orient="horizontal", length=200, mode="determinate")
            #progress.place(x=200, y=370)
            #progress["value"] = 20
            print("log: running download script!")
            #progress["value"] = 40
            subprocess.run(f"gh run list -R Frogging-Family/wine-tkg-git -w proton-arch-nopackage.yml -s success -L 1 --json databaseId | jq -r '.[0].databaseId' | xargs -I {{}} gh run download {{}} -R Frogging-Family/wine-tkg-git -D {download_dir_selection}", shell=True)
            #progress["value"] = 60
            download_dir = download_dir_selection
            download_path = os.path.join(download_dir, "proton-tkg-build")
            #progress["value"] = 70
            print("log: Extracting with Subprocess (if it fails make sure you have tar installed!)")
            subprocess.run(f"tar -xf {download_dir}proton-tkg-build/*.tar -C {download_dir}", shell=True)
            #progress["value"] = 80
            SuccessLabel = ttk.Label(root, text="Installed Successfully!", style="GreenFartation.TLabel")
            SuccessLabel.place(x=530, y=370)
            subprocess.run(f"rm -rf {download_path}", shell=True)
            #progress["value"] = 100
            time.sleep(2)
            print("log: Completed!")
            #progress.place_forget()
        except subprocess.CalledProcessError:
            #progress["value"] = 0
            messagebox.showerror("Error!", "Check Internet Connection or Curl/WGet/Tar/GH Installation!")
            time.sleep(2)
            #progress.place_forget()
    if selected == "TKG Proton Experimental":
        try:
            print("log: selected TKG Proton Experimental, continuuing")
            #progress.place(x=200, y=370)
            #progress["value"] = 20
            print("log: running download script!")
            #progress["value"] = 40
            subprocess.run(f"gh run list -R Frogging-Family/wine-tkg-git -w proton-valvexbe-arch-nopackage.yml -s success -L 1 --json databaseId | jq -r '.[0].databaseId' | xargs -I {{}} gh run download {{}} -R Frogging-Family/wine-tkg-git -D {download_dir_selection}", shell=True)
            #progress["value"] = 60
            download_dir = download_dir_selection
            #progress["value"] = 70
            download_path = os.path.join(download_dir, "proton-tkg-build")
            print("log: Extracting with Subprocess (if it fails make sure you have tar installed!)")
            subprocess.run(f"tar -xf {download_dir}proton-tkg-build/*.tar -C {download_dir}", shell=True)
            #progress["value"] = 80
            SuccessLabel = ttk.Label(root, text="Installed Successfully!", style="GreenFartation.TLabel")
            SuccessLabel.place(x=530, y=370)
            subprocess.run(f"rm -rf {download_path}", shell=True)
            #progress["value"] = 100
            time.sleep(2)
            print("log: Completed!")
            #progress.place_forget()
        except subprocess.CalledProcessError:
            #progress["value"] = 0
            messagebox.showerror("Error!", "Check Internet Connection or Curl/WGet/Tar/GH Installation!")
            time.sleep(2)
            #progress.place_forget()

def download_proton_background():
    download_thread = threading.Thread(target=download_proton)
    download_thread.start()

style = ttk.Style()
style.configure("GreenFartation.TLabel", foreground="green")
style.configure("Green.TButton", foreground="green")
style.configure("Red.TButton", foreground="red")

btnReadDescription = ttk.Button(root, text="Read Description", command=openDescription)
btnReadDescription.place(x=530, y=250)

btnInstall = ttk.Button(root, text="Install! ✅", style="Green.TButton", command=download_proton_background)
btnInstall.place(x=550, y=300)

btnSettings = ttk.Button(root, text="Settings", command=options)
btnSettings.place(x=30, y=20)

btnPlaySong = ttk.Button(root, text="🔊", command=playSound_background)
btnPlaySong.place(x=630, y=15)

btnQuit = ttk.Button(root, text="Quit", style="Red.TButton",command=full_quit)
btnQuit.place(x=35, y=350)
print("log: Fully Loaded")
root.mainloop()

# Made by MikuYoshikage

import sys
import logic
from pathlib import Path
from PIL import Image
import time
import traceback

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QGroupBox,
    QDialog,
    QScrollArea,
    QFrame,
    QFileDialog
)
from PySide6.QtCore import Qt, QObject, Signal, QThread
from PySide6.QtGui import QIcon

APP_WIDTH = 500
APP_HEIGHT = 750

trackList=[]

modNameValid = False
modIdValid = False


class TrackWidget(QFrame):

    def __init__(self, track_id, track_name, sound_path, texture_path):
        super().__init__()

        self.track_id = track_id
        self.track_name = track_name
        self.sound_path = sound_path
        self.texture_path = texture_path

        self.idLabel = QLabel(f"ID: {track_id}")
        self.nameLabel = QLabel(f"Name: {track_name}")
        self.soundLabel = QLabel(f"Sound: {sound_path}")
        self.textureLabel = QLabel(f"Texture: {texture_path}")

        self.removeButton = QPushButton("Remove")

        layout = QVBoxLayout()

        layout.addWidget(
            self.idLabel,
            alignment=Qt.AlignmentFlag.AlignLeft
        )

        layout.addWidget(
            self.nameLabel,
            alignment=Qt.AlignmentFlag.AlignLeft
        )

        layout.addWidget(
            self.soundLabel,
            alignment=Qt.AlignmentFlag.AlignLeft
        )

        layout.addWidget(
            self.textureLabel,
            alignment=Qt.AlignmentFlag.AlignLeft
        )

        buttonLayout = QHBoxLayout()

        buttonLayout.addWidget(self.removeButton)
        buttonLayout.addStretch()

        layout.addLayout(buttonLayout)

        self.setLayout(layout)

        self.removeButton.clicked.connect(self.removeTrack)

    def removeTrack(self):
        global trackList

        trackList = [
            track
            for track in trackList
            if track.id != self.track_id
        ]

        updateTrackList()
        updateGenerateButton()
    


class AddTrackDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Add Track")
        self.setFixedSize(500, 400)
        self.setWindowIcon(QIcon("gui_things/icon.png"))

        self.idValid = False
        self.nameValid = False
        self.soundValid = False
        self.textureValid = False

        layout = QVBoxLayout()

        self.idInput = QLineEdit()
        self.idInput.setPlaceholderText("Enter track ID")

        self.idValidCh = QPushButton("Verify")

        idLayout = QHBoxLayout()
        idLayout.addWidget(self.idInput)
        idLayout.addWidget(self.idValidCh)

        layout.addWidget(QLabel("Track ID:"))
        layout.addLayout(idLayout)

        self.nameInput = QLineEdit()
        self.nameInput.setPlaceholderText("Enter track name")

        self.nameValidCh = QPushButton("Verify")

        nameLayout = QHBoxLayout()
        nameLayout.addWidget(self.nameInput)
        nameLayout.addWidget(self.nameValidCh)

        layout.addWidget(QLabel("Track name:"))
        layout.addLayout(nameLayout)


        self.soundInput = QLineEdit()
        self.soundInput.setReadOnly(True)

        self.soundButton = QPushButton("Choose sound")

        soundLayout = QHBoxLayout()
        soundLayout.addWidget(self.soundInput)
        soundLayout.addWidget(self.soundButton)

        layout.addWidget(QLabel("Sound:"))
        layout.addLayout(soundLayout)


        self.textureInput = QLineEdit()
        self.textureInput.setReadOnly(True)

        self.textureButton = QPushButton("Choose texture")

        textureLayout = QHBoxLayout()
        textureLayout.addWidget(self.textureInput)
        textureLayout.addWidget(self.textureButton)

        layout.addWidget(QLabel("Texture:"))
        layout.addLayout(textureLayout)


        self.addButton = QPushButton("Add")
        self.cancelButton = QPushButton("Cancel")

        self.addButton.setEnabled(False)

        buttonsLayout = QHBoxLayout()
        buttonsLayout.addWidget(self.cancelButton)
        buttonsLayout.addWidget(self.addButton)

        layout.addLayout(buttonsLayout)

        self.setLayout(layout)


        self.idValidCh.clicked.connect(self.verifyId)
        self.nameValidCh.clicked.connect(self.verifyName)

        self.soundButton.clicked.connect(self.chooseSound)
        self.textureButton.clicked.connect(self.chooseTexture)

        self.idInput.textChanged.connect(self.resetIdValidation)
        self.nameInput.textChanged.connect(self.resetNameValidation)

        self.cancelButton.clicked.connect(self.reject)
        self.addButton.clicked.connect(self.tryAdd)



    def verifyId(self):
        global trackList
        if logic.is_valid_id(self.idInput.text()) and logic.is_unique_track_id(trackList, self.idInput.text()):
            self.idValid = True
            self.idInput.setStyleSheet("color: #00ff00;")
        else:
            self.idValid = False
            self.idInput.setStyleSheet("color: #ff0000;")

        self.updateAddButton()

    def resetIdValidation(self):
        self.idValid = False
        self.idInput.setStyleSheet("color: white;")

        self.updateAddButton()


    def verifyName(self):
        if logic.is_english_text(self.nameInput.text()):
            self.nameValid = True
            self.nameInput.setStyleSheet("color: #00ff00;")
        else:
            self.nameValid = False
            self.nameInput.setStyleSheet("color: #ff0000;")

        self.updateAddButton()

    def resetNameValidation(self):
        self.nameValid = False
        self.nameInput.setStyleSheet("color: white;")

        self.updateAddButton()


    def chooseSound(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose sound",
            "",
            "Audio Files (*.mp3 *.ogg)"
        )

        if not path:
            return

        soundPath = Path(path)

        self.soundInput.setText(path)

        if not soundPath.exists():
            self.soundValid = False
            self.soundInput.setStyleSheet("color: #ff0000;")
            self.updateAddButton()
            return

        if soundPath.suffix.lower() not in [".mp3", ".ogg"]:
            self.soundValid = False
            self.soundInput.setStyleSheet("color: #ff0000;")
            self.updateAddButton()
            return

        self.soundValid = True
        self.soundInput.setStyleSheet("color: #00ff00;")

        self.updateAddButton()


    def chooseTexture(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose texture",
            "",
            "PNG Images (*.png)"
        )

        if not path:
            return

        texturePath = Path(path)

        self.textureInput.setText(path)

        if not texturePath.exists():
            self.textureValid = False
            self.textureInput.setStyleSheet("color: #ff0000;")
            self.updateAddButton()
            return

        if texturePath.suffix.lower() != ".png":
            self.textureValid = False
            self.textureInput.setStyleSheet("color: #ff0000;")
            self.updateAddButton()
            return

        try:
            with Image.open(texturePath) as image:

                if image.size not in [(16, 16), (64, 64)]:
                    self.textureValid = False
                    self.textureInput.setStyleSheet("color: #ff0000;")
                    self.updateAddButton()
                    return

        except Exception:
            self.textureValid = False
            self.textureInput.setStyleSheet("color: #ff0000;")
            self.updateAddButton()
            return

        self.textureValid = True
        self.textureInput.setStyleSheet("color: #00ff00;")

        self.updateAddButton()


    def updateAddButton(self):
        self.addButton.setEnabled(
            self.idValid
            and self.nameValid
            and self.soundValid
            and self.textureValid
        )


    def tryAdd(self):

        if not (
            self.idValid
            and self.nameValid
            and self.soundValid
            and self.textureValid
        ):
            return

        self.accept()


    def getTrack(self):
        return logic.Track(
            id=self.idInput.text(),
            name=self.nameInput.text(),
            sound_path=self.soundInput.text(),
            texture_path=self.textureInput.text(),
        )
    
class ValidationRulesDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Validation Rules")
        self.setFixedSize(450, 650)
        self.setWindowIcon(QIcon("gui_things/icon.png"))

        layout = QVBoxLayout()

        namesTitle = QLabel("Mod / Track names")
        namesTitle.setStyleSheet("font-size: 20px; font-weight: bold;")

        namesRules = QLabel(
            "English letters only<br>"
            "Spaces, apostrophes (') and hyphens (-) are allowed<br>"
            "Maximum 50 characters"
        )

        idsTitle = QLabel("Mod / Track IDs")
        idsTitle.setStyleSheet("font-size: 20px; font-weight: bold;")

        idsRules = QLabel(
            "Lowercase English letters only<br>"
            "Underscores (_) are allowed<br>"
            "unique track IDs are required<br>"
            "Maximum 50 characters"
        )

        tracksTitle = QLabel("Tracks")
        tracksTitle.setStyleSheet("font-size: 20px; font-weight: bold;")

        tracksRules = QLabel(
            "At least 1 track is required<br>"
            "Maximum 128 tracks"
        )

        soundTitle = QLabel("Sound files")
        soundTitle.setStyleSheet("font-size: 20px; font-weight: bold;")

        soundRules = QLabel(
            "MP3 (.mp3) or OGG (.ogg)<br>"
            "The selected file must exist"
        )

        textureTitle = QLabel("Texture files")
        textureTitle.setStyleSheet("font-size: 20px; font-weight: bold;")

        textureRules = QLabel(
            "PNG (.png) only<br>"
            "Resolution must be 16×16 or 64×64 pixels<br>"
            "The selected file must exist"
        )

        layout.addWidget(namesTitle)
        layout.addWidget(namesRules)

        layout.addSpacing(15)

        layout.addWidget(idsTitle)
        layout.addWidget(idsRules)

        layout.addSpacing(15)

        layout.addWidget(tracksTitle)
        layout.addWidget(tracksRules)

        layout.addSpacing(15)

        layout.addWidget(soundTitle)
        layout.addWidget(soundRules)

        layout.addSpacing(15)

        layout.addWidget(textureTitle)
        layout.addWidget(textureRules)

        layout.addStretch()

        closeButton = QPushButton("Close")
        closeButton.clicked.connect(self.accept)

        layout.addWidget(closeButton)

        self.setLayout(layout)



class GenerationWorker(QObject):

    statusChanged = Signal(str)
    finished = Signal(bool, str)
    closeRequested = Signal()

    def __init__(self, mod):
        super().__init__()

        self.mod = mod

    def write_log(self, message):
        log_path = Path("gui_things/log.txt")

        with open(log_path, "a", encoding="utf-8") as log:
            log.write(message)
            log.write("\n")

    def run(self):
        try:

            self.statusChanged.emit("Generating mod files...")
            logic.Start_Create()

            self.statusChanged.emit("Changing Gradle settings...")
            logic.change_property(self.mod)

            self.statusChanged.emit("Filling Java files...")
            logic.fill_java_placeholders(self.mod)

            self.statusChanged.emit("Moving sound files...")

            failed_sounds, failed_reasons = logic.move_records(self.mod)

            if failed_sounds:

                self.write_log(
                    "Failed to process sound files:\n"
                    + "\n".join(f"Track ID: {track_id}, Reason: {reason}" for track_id, reason in zip(failed_sounds, failed_reasons))
                )
                
                self.statusChanged.emit("Failed to process some sound files. See gui_things/log.txt")

                logic.delete_failed_sounds(
                    failed_sounds,
                    self.mod
                )

                if not self.mod.tracks:

                    self.write_log(
                        "All tracks failed to process."
                    )

                    self.finished.emit(
                        False,
                        "All tracks failed to process."
                    )

                    return

            self.statusChanged.emit("Moving texture files...")
            logic.move_textures(self.mod)

            self.statusChanged.emit("Generating JSON files...")

            logic.generate_en_us_json(self.mod)
            logic.generate_models_item_jsons(self.mod)
            logic.generate_music_discs_json(self.mod)
            logic.generate_sounds_json(self.mod)

            self.statusChanged.emit("Building the mod...")

            build_result = logic.build_mod()

            if not build_result["success"]:

                self.write_log(
                    "Mod build failed.\n\n"
                    "--- STDOUT ---\n"
                    + build_result["stdout"][-2000:]
                    + "\n\n"
                    "--- STDERR ---\n"
                    + build_result["stderr"][-1500:]
                    + "\n"
                )

                self.finished.emit(
                    False,
                    "Mod build failed. See gui_things/log.txt"
                )

                return


            built_jar = logic.find_built_jar()

            if built_jar:

                success_message = (
                    "Mod built successfully!\n"
                    f"Built JAR: {built_jar}"
                )

            else:

                self.write_log(
                    "Mod was built successfully, "
                    "but the built JAR could not be found."
                )

                success_message = (
                    "Mod built, but JAR file could not be found."
                )


            self.finished.emit(
                True,
                success_message
            )

            self.statusChanged.emit(
                success_message + "\nClosing in 10 seconds..."
            )

            time.sleep(10)

            self.closeRequested.emit()

        except Exception as e:

            self.write_log(
                "Unexpected error during generation:\n\n"
                + traceback.format_exc()
            )

            self.finished.emit(
                False,
                "Generation failed. See gui_things/log.txt"
            )


def clear_log():
    log_path = Path("gui_things/log.txt")

    with open(log_path, "w", encoding="utf-8"):
        pass


def load_stylesheet(app, filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())

def clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()

        if widget is not None:
            widget.deleteLater()

clear_log()

app = QApplication(sys.argv)
load_stylesheet(app, "gui_things/style.qss")

window = QWidget()
window.setWindowTitle("MY's Mod Maker")
window.setFixedSize(APP_WIDTH, APP_HEIGHT)
window.setWindowIcon(QIcon("gui_things/icon.png"))

layout = QVBoxLayout()
layout.setContentsMargins(25, 25, 25, 25)
layout.setSpacing(12)

welcomeLabel = QLabel("Welcome to the MY's Mod Maker GUI!")
welcomeLabel.setObjectName("headerLabel")

validatorButton = QPushButton("Validation rules")
def showValidationRules():
    dialog = ValidationRulesDialog()
    dialog.exec()

modNameLayout = QHBoxLayout()
modNameInput = QLineEdit()
modNameInput.setPlaceholderText("Enter mod name:")
validatorModNameButton = QPushButton("Verify")

def verifyModName():
    global modNameValid

    if logic.is_english_text(modNameInput.text()):
        modNameInput.setStyleSheet("color: #00ff00;")
        modNameValid = True
        updateGenerateButton()
    else:
        modNameInput.setStyleSheet("color: #ff0000;")
        modNameValid = False
    

def resetModName():
    global modNameValid

    modNameValid = False
    modNameInput.setStyleSheet("color: white;")
    updateGenerateButton()

modNameLayout.addWidget(modNameInput)
modNameLayout.addWidget(validatorModNameButton)

modIdLayout = QHBoxLayout()
modIdInput = QLineEdit()
modIdInput.setPlaceholderText("Enter mod ID:")
validatorModIdButton = QPushButton("Verify")

def verifyModId():
    global modIdValid

    if logic.is_valid_id(modIdInput.text()):
        modIdInput.setStyleSheet("color: #00ff00;")
        modIdValid = True
        updateGenerateButton()
    else:
        modIdInput.setStyleSheet("color: #ff0000;")
        modIdValid = False

def resetModId():
    global modIdValid

    modIdValid = False
    modIdInput.setStyleSheet("color: white;")
    updateGenerateButton()


modIdLayout.addWidget(modIdInput)
modIdLayout.addWidget(validatorModIdButton)

tracksBox = QGroupBox("Tracks")

scrollArea = QScrollArea()
scrollArea.setWidgetResizable(True)
scrollArea.setMinimumHeight(250)

tracksContainer = QWidget()
tracksLayout = QVBoxLayout()

tracksContainer.setLayout(tracksLayout)

scrollArea.setWidget(tracksContainer)

tracksBoxLayout = QVBoxLayout()
tracksBoxLayout.addWidget(scrollArea)

tracksBox.setLayout(tracksBoxLayout)

updateTrackListBt = QPushButton("Update TrackList")

def updateTrackList():
    clear_layout(tracksLayout)
    for x in trackList:
        tracksLayout.addWidget(TrackWidget(x.id,x.name,x.sound_path,x.texture_path))
    updateGenerateButton()


openAddTrackButtonWin = QPushButton("Add Track")

def addTrackWin():
    dialog = AddTrackDialog()

    if dialog.exec() == QDialog.DialogCode.Accepted:
        track = dialog.getTrack()
        trackList.append(track)

        updateTrackList()
        updateGenerateButton()

generateModButton = QPushButton("Generate Mod")
generateModButton.setEnabled(False)
generateModLabel = QLabel("Generation Status: generation hasn't started yet")

def updateGenerateButton():
    generateModButton.setEnabled(
        modNameValid
        and modIdValid
        and len(trackList) > 0
        and len(trackList) <=128
    )

def generateMod():


    if not modNameValid:
        generateModLabel.setText(
            "Generation Status: mod name is not valid."
        )
        return

    if not modIdValid:
        generateModLabel.setText(
            "Generation Status: mod ID is not valid."
        )
        return

    if len(trackList) == 0:
        generateModLabel.setText(
            "Generation Status: add at least one track."
        )
        return

    if len(trackList) > 128:
        generateModLabel.setText(
            "Generation Status: maximum 128 tracks."
        )
        return

    mod = logic.Mod(
        id=modIdInput.text(),
        name=modNameInput.text(),
        tracks=trackList.copy()
    )

    generateModButton.setEnabled(False)

    generateModLabel.setText(
        "Generation Status: starting..."
    )

    window.generationThread = QThread()

    window.generationWorker = GenerationWorker(mod)

    window.generationWorker.moveToThread(
        window.generationThread
    )

    window.generationThread.started.connect(
        window.generationWorker.run
    )

    window.generationWorker.statusChanged.connect(
        lambda text: generateModLabel.setText(
            f"Generation Status: {text}"
        )
    )

    def generationFinished(success, message):

        generateModLabel.setText(
            f"Generation Status: {message}"
        )

        if not success:
            generateModButton.setEnabled(True)

    window.generationWorker.finished.connect(
        generationFinished
    )

    window.generationWorker.closeRequested.connect(
        window.close
    )
    window.generationWorker.finished.connect(
        window.generationThread.quit
    )
    window.generationThread.finished.connect(
        window.generationWorker.deleteLater
    )

    window.generationThread.finished.connect(
        window.generationThread.deleteLater
    )
    window.generationThread.start()


layout.addWidget(welcomeLabel)
layout.addSpacing(15)
layout.addWidget(validatorButton)

layout.addLayout(modNameLayout)
layout.addLayout(modIdLayout)

layout.addWidget(tracksBox)

layout.addWidget(updateTrackListBt)

layout.addWidget(openAddTrackButtonWin)

layout.addStretch()
layout.addWidget(generateModButton, alignment=Qt.AlignmentFlag.AlignCenter)
layout.addWidget(generateModLabel, alignment=Qt.AlignmentFlag.AlignCenter)


updateTrackListBt.clicked.connect(updateTrackList)
openAddTrackButtonWin.clicked.connect(addTrackWin)
validatorButton.clicked.connect(showValidationRules)
validatorModNameButton.clicked.connect(verifyModName)
validatorModIdButton.clicked.connect(verifyModId)
generateModButton.clicked.connect(generateMod)

modNameInput.textChanged.connect(resetModName)
modIdInput.textChanged.connect(resetModId)

window.setLayout(layout)
window.show()

sys.exit(app.exec())
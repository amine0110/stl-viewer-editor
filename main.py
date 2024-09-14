from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton,
    QFileDialog, QMessageBox, QHBoxLayout
)
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D STL Editor with Interactive Clipping Plane and Undo")
        self.initUI()

        # Variables to store the loaded STL actor and filename
        self.current_actor = None
        self.filename = None

        # Clipping plane and widget
        self.clipping_plane = vtk.vtkPlane()
        self.plane_widget = None

        # Original PolyData for undo functionality
        self.original_polydata = None

        # Flag to indicate if clipping is enabled
        self.clipping_enabled = False

    def initUI(self):
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.layout = QVBoxLayout()

        # VTK Widget
        self.vtkWidget = QVTKRenderWindowInteractor(self.centralWidget)
        self.layout.addWidget(self.vtkWidget)

        # Buttons Layout
        buttons_layout = QHBoxLayout()

        # Load STL Button
        self.loadButton = QPushButton("Load STL")
        buttons_layout.addWidget(self.loadButton)
        self.loadButton.clicked.connect(self.open_file_dialog)

        # Enable Clipping Plane Button
        self.enableClipButton = QPushButton("Enable Clipping")
        buttons_layout.addWidget(self.enableClipButton)
        self.enableClipButton.clicked.connect(self.toggle_clipping_plane)

        # Undo Clipping Button
        self.undoButton = QPushButton("Undo Clipping")
        self.undoButton.setEnabled(False)
        buttons_layout.addWidget(self.undoButton)
        self.undoButton.clicked.connect(self.undo_clipping)

        # Export STL Button
        self.exportButton = QPushButton("Export STL")
        buttons_layout.addWidget(self.exportButton)
        self.exportButton.clicked.connect(self.export_stl)

        self.layout.addLayout(buttons_layout)

        self.centralWidget.setLayout(self.layout)

        # VTK Renderer setup
        self.renderer = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)

        # Set a more responsive interactor style
        self.interactor = self.vtkWidget.GetRenderWindow().GetInteractor()
        interactor_style = vtk.vtkInteractorStyleTrackballCamera()
        self.interactor.SetInteractorStyle(interactor_style)

        self.show()

    def open_file_dialog(self):
        options = QFileDialog.Options()
        self.filename, _ = QFileDialog.getOpenFileName(
            self, "Open STL File", "", "STL Files (*.stl);;All Files (*)", options=options
        )
        if self.filename:
            self.load_stl_file(self.filename)

    def load_stl_file(self, filename):
        # Remove any existing actor
        if self.current_actor:
            self.renderer.RemoveActor(self.current_actor)

        # Load STL file
        reader = vtk.vtkSTLReader()
        reader.SetFileName(filename)
        reader.Update()

        # Store the original polydata for undo functionality
        self.original_polydata = reader.GetOutput()

        # Mapper
        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputData(self.original_polydata)

        # Actor
        self.current_actor = vtk.vtkActor()
        self.current_actor.SetMapper(self.mapper)

        # Add the actor to the scene
        self.renderer.AddActor(self.current_actor)
        self.renderer.ResetCamera()
        self.vtkWidget.GetRenderWindow().Render()
        self.interactor.Initialize()

        # Disable previous plane widget if any
        if self.plane_widget:
            self.plane_widget.Off()
            self.plane_widget = None

        # Reset clipping state
        self.clipping_enabled = False
        self.enableClipButton.setText("Enable Clipping")
        self.undoButton.setEnabled(False)

    def toggle_clipping_plane(self):
        if not self.current_actor:
            QMessageBox.warning(self, "Error", "No STL file loaded.")
            return

        if not self.clipping_enabled:
            # Enable the clipping plane
            self.create_clipping_plane_widget()
            self.clipping_enabled = True
            self.enableClipButton.setText("Disable Clipping")
            self.undoButton.setEnabled(True)
        else:
            # Disable the clipping plane
            self.disable_clipping_plane()
            self.clipping_enabled = False
            self.enableClipButton.setText("Enable Clipping")
            self.undoButton.setEnabled(False)

    def create_clipping_plane_widget(self):
        # Create the clipping plane
        self.clipping_plane = vtk.vtkPlane()

        # Create the plane widget
        self.plane_widget = vtk.vtkImplicitPlaneWidget()
        self.plane_widget.SetInteractor(self.interactor)
        self.plane_widget.SetPlaceFactor(1.25)  # Makes the widget slightly larger than the actor
        self.plane_widget.SetInputData(self.original_polydata)
        self.plane_widget.PlaceWidget()
        self.plane_widget.AddObserver("InteractionEvent", self.on_plane_widget_interaction)
        self.plane_widget.On()

        # Initial clipping
        self.on_plane_widget_interaction(None, None)

    def disable_clipping_plane(self):
        # Remove the clipping plane widget
        if self.plane_widget:
            self.plane_widget.Off()
            self.plane_widget = None

        # Reset the mapper to the original data
        self.mapper.SetInputData(self.original_polydata)
        self.vtkWidget.GetRenderWindow().Render()

    def on_plane_widget_interaction(self, caller, event):
        # Update the clipping plane based on the widget's parameters
        self.plane_widget.GetPlane(self.clipping_plane)

        # Apply the clipping plane to the mapper via a filter
        clipper = vtk.vtkClipPolyData()
        clipper.SetInputData(self.original_polydata)
        clipper.SetClipFunction(self.clipping_plane)
        clipper.Update()

        # Check if the output of the clipper is empty
        if clipper.GetOutput().GetNumberOfCells() == 0:
            # Do not update the mapper if clipping results in empty data
            return

        # Update the mapper with the clipped data
        self.mapper.SetInputData(clipper.GetOutput())
        self.vtkWidget.GetRenderWindow().Render()

    def undo_clipping(self):
        # Reset the mapper to the original data
        self.mapper.SetInputData(self.original_polydata)
        self.vtkWidget.GetRenderWindow().Render()

        # Reset the plane widget to initial state
        if self.plane_widget:
            self.plane_widget.PlaceWidget()
            self.on_plane_widget_interaction(None, None)

    def export_stl(self):
        if not self.current_actor:
            QMessageBox.warning(self, "Error", "No STL file loaded or edited.")
            return

        # Save file dialog
        save_filename, _ = QFileDialog.getSaveFileName(
            self, "Save STL File", "", "STL Files (*.stl);;All Files (*)"
        )
        if not save_filename:
            return

        # Extract the polydata from the mapper
        polydata = self.mapper.GetInput()

        # Write the polydata to an STL file
        writer = vtk.vtkSTLWriter()
        writer.SetFileName(save_filename)
        writer.SetInputData(polydata)
        writer.Write()

        QMessageBox.information(self, "Success", "STL file exported successfully.")

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()

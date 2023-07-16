from PySide6.QtCore import *
from PySide6.QtWidgets import *

from core.exponentialnumber import ExponentialNumber
from core.tasksetdata import TaskSetData

from lib.native.taskworker import TaskWorker

from ui.native.scanarea import ScanArea
from ui.native.scientificspinbox import ScientificSpinBox
from ui.native.tasksetlist import TaskSetList
from ui.native.taskset.tasksetstatus import TaskSetStatus
from ui.native.togglebutton import ToggleButton


class Ui_MainWindow(QMainWindow):
    """    
        The main user interface class for the STM Automator application.

        This class represents the main window of the STM Automator application. It provides a graphical user interface to
        control scanning tunneling microscope (STM) experiments. It provides functionality to configure scanning parameters, 
        spectroscopy parameters, and  sweep options, as well as manage and execute task sets in a multithreaded manner.
        The class sets up various components of the application, such as the toolbar, scan area, task list, and options frames. 
        It also handles event connections for different UI elements and manages the execution of tasks.

        The class inherits from QMainWindow, a top-level application window class in Qt. It serves as the main container
        for the UI elements and layouts.

        Attributes:
            centralwidget (QWidget): The central widget for the main window.
            threadpool (QThreadPool): A thread pool used for running tasks in the background.
            running (bool): Flag indicating if a task is currently running.
            paused (bool): Flag indicating if the task execution is paused.
            content (QFrame): The content frame containing the main application elements.
            scan_area_frame (QFrame): The frame containing the scan area visualization.
            scan_area (ScanArea): The widget responsible for displaying the scan area.
            options_frame (QFrame): The frame containing the options and task-related controls.
            task_set_list (TaskSetList): The list of task sets displayed in the user interface.

        Methods:
            __init__: Initializes the main window and sets up the user interface.
            setup_events: Sets up event connections for buttons and input fields.
            play_clicked: Starts the task execution when the "Play" button is clicked.
            pause_clicked: Pauses the task execution when the "Pause" button is clicked.
            add_task_set: Adds a new task set to the task set list when the "Add Task Set" button is clicked.
            update_scan_size: Updates the scan area size based on the value entered in the "Size" input field.
            update_scan_position: Updates the scan area position based on the values entered in the "X offset" and "Y offset" input fields.
            scan_rect_moved: Updates the "X offset," "Y offset," and "Size" input fields when the scan area is moved.
            update_time_to_finish: Updates the estimated time to finish the task execution based on input field values.
            update_total_images: Updates the total number of images based on input field values.
            set_sweep_enabled: Enables or disables the sweep-related input fields based on the selected sweep parameter.
            set_sweep_units: Sets the units for sweep-related input fields based on the selected sweep parameter.
            set_sweep_vals: Sets the sweep-related input fields' values based on the selected sweep parameter.
            update_sweep_params: Updates the sweep-related parameters based on the selected sweep parameter.
            set_enable_spectroscopy: Enables or disables spectroscopy-related input fields based on the selected spectroscopy mode.

        Note:
        - This class uses PySide6, a Python binding for the Qt framework, to create the graphical user interface.
        - It defines the layout and behavior of the STM Automator application's main window.
        - The code relies on custom widgets and classes imported from various modules to build the user interface.
        - The "scan_area" and "options_frame" widgets are used to visualize the scan area and configure scan options, respectively.
        - The "task_set_list" displays a list of task sets that the user can add and execute.
        - The "play_clicked" method initiates the execution of tasks in the background using a thread pool.
        - The "pause_clicked" method pauses the task execution.
        - The "add_task_set" method adds a new task set to the list based on user-provided parameters.
        - The "update_scan_size," "update_scan_position," and "scan_rect_moved" methods update the scan area visualization based on user inputs.
        - The "update_time_to_finish" and "update_total_images" methods calculate and display task-related statistics.
        - The "set_sweep_enabled," "set_sweep_units," and "set_sweep_vals" methods manage sweep-related input fields.
        - The "update_sweep_params" method updates sweep-related input fields based on the selected sweep parameter.
        - The "set_enable_spectroscopy" method enables or disables spectroscopy-related input fields based on the selected mode.
    """
    def __init__(self, *args, **kwargs):
        """
            Initialize the main window UI.

            This method sets up the main window and its components, including the toolbar, content frame, scan area, and
            various widgets. It also configures the initial states of different UI elements and establishes event
            connections.
        """
        super().__init__(*args, **kwargs)

        ## ------ Window Settings ------ ##
        self.setWindowTitle("STM Automator")
        self.resize(1400, 800)
        self.centralwidget = QWidget(self)

        ## ------- Task threadpool ----- ##
        self.running = False
        self.paused = False
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        ## ------ Toolbar ------ ##
        self.toolbar = QFrame(self.centralwidget, objectName='toolbar')
        self.toolbar.setFixedHeight(26)

        self.menu = ToggleButton(objectName='bars')
        self.left_space = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.play = ToggleButton(objectName='play')
        self.pause = ToggleButton(objectName='pause')
        self.stop = ToggleButton(objectName='stop')
        self.right_space = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.settings = ToggleButton(objectName='cog')

        self.menu.setCheckable(False)
        self.settings.setCheckable(False)

        button_group = QFrame(objectName='button_group')
        button_group.setFixedHeight(26)
        button_group.setLayout(QHBoxLayout())
        button_group.layout().setContentsMargins(0,0,0,0)
        button_group.layout().addWidget(self.play)
        button_group.layout().addWidget(self.pause)
        button_group.layout().addWidget(self.stop)
        
        self.toolbar_layout = QHBoxLayout(self.toolbar)
        self.toolbar_layout.setSpacing(0)
        self.toolbar_layout.setContentsMargins(0, 0, 0, 0)
        self.toolbar_layout.addWidget(self.menu)
        self.toolbar_layout.addItem(self.left_space)
        self.toolbar_layout.addWidget(button_group)
        # self.toolbar_layout.addWidget(self.play)
        # self.toolbar_layout.addWidget(self.pause)
        # self.toolbar_layout.addWidget(self.stop)
        self.toolbar_layout.addItem(self.right_space)
        self.toolbar_layout.addWidget(self.settings)

        ## ---------- Content ----------##
        self.content = QFrame(self.centralwidget, objectName="content_frame")

        ## Scan Area
        self.scan_area_frame = QFrame(self.content, objectName="scan_area_frame")
        self.scan_area_frame.setMinimumWidth(500)
        
        self.scan_area = ScanArea(self.scan_area_frame)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        sizePolicy.setHeightForWidth(True)
        self.scan_area.setSizePolicy(sizePolicy)

        self.scan_area_layout = QVBoxLayout(self.scan_area_frame)
        self.scan_area_layout.setContentsMargins(0, 7, 0, 0)
        # self.scan_area_layout.addStretch()
        self.scan_area_layout.addWidget(self.scan_area)
        # self.scan_area_layout.addStretch()

        ## Options
        self.options_frame = QFrame(self.content, objectName="options_frame")
        self.options_frame.setMinimumWidth(350)
        self.options_frame.setMaximumWidth(375)

        # Scan Options
        self.scan_options = QGroupBox("Image Parameters")
        self.scan_options.setFlat(True)
        self.scan_options.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lines_per_frame_label = QLabel("Lines per frame")
        self.lines_per_frame = QComboBox()
        self.lines_per_frame.addItems([f'{2**n}' for n in range(3, 13)])
        self.lines_per_frame.setCurrentIndex(5)
        self.lines_per_frame.setFixedWidth(150)
        
        self.bias_label = QLabel("Bias")
        self.bias = ScientificSpinBox()
        self.bias.setBounds(lower=ExponentialNumber(-5, 0), upper=ExponentialNumber(5, 0))
        self.bias.setValue(ExponentialNumber(300, -3))
        self.bias.setUnits('V')
        
        self.set_point_label = QLabel("Set point current")
        self.set_point = ScientificSpinBox()
        self.set_point.setBounds(lower=ExponentialNumber(-500, -9), upper=ExponentialNumber(500, -9))
        self.set_point.setValue(ExponentialNumber(100, -12))
        self.set_point.setUnits('A')

        self.scan_size_label = QLabel("Size")
        self.scan_size = ScientificSpinBox()
        self.scan_size.setBounds(lower=ExponentialNumber(2.5, -12), upper=ExponentialNumber(3, -6))
        self.scan_size.setValue(ExponentialNumber(100, -9))
        self.scan_size.setUnits('m')

        self.x_offset_label = QLabel("X offset")
        self.x_offset = ScientificSpinBox()
        self.x_offset.setBounds(lower=ExponentialNumber(-1.5, -6), upper=ExponentialNumber(1.5, -6))
        self.x_offset.setValue(ExponentialNumber(0, -9))
        self.x_offset.setUnits('m')

        self.y_offset_label = QLabel("Y offset")
        self.y_offset = ScientificSpinBox()
        self.y_offset.setBounds(lower=ExponentialNumber(-1.5, -6), upper=ExponentialNumber(1.5, -6))
        self.y_offset.setValue(ExponentialNumber(0, -9))
        self.y_offset.setUnits('m')

        self.scan_speed_label = QLabel("Scan speed")
        self.scan_speed = ScientificSpinBox()
        self.scan_speed.setBounds(lower=ExponentialNumber(2.5, -12), upper=ExponentialNumber(1, -6))
        self.scan_speed.setValue(ExponentialNumber(100, -9))
        self.scan_speed.setUnits('m/s')
        self.scan_speed.setEnabled(False)

        self.line_time_label = QLabel("Line time")
        self.line_time = ScientificSpinBox()
        self.line_time.setBounds(lower=ExponentialNumber(2.5, -12), upper=ExponentialNumber(1000, 0))
        self.line_time.setValue(ExponentialNumber(1, 0))
        self.line_time.setUnits('s')

        self.repetitions_label = QLabel("Repetitions")
        self.repetitions = QSpinBox()
        self.repetitions.setValue(1)
        self.repetitions.setMinimum(1)
        
        img_param_widgets = [(self.bias_label, self.bias),
                             (self.set_point_label, self.set_point),
                             (self.scan_size_label, self.scan_size),
                             (self.x_offset_label, self.x_offset),
                             (self.y_offset_label, self.y_offset),
                             (self.scan_speed_label, self.scan_speed),
                             (self.line_time_label, self.line_time),
                             (self.lines_per_frame_label, self.lines_per_frame),
                             (self.repetitions_label, self.repetitions)]
        
        self.scan_options_layout = QGridLayout()
        self.scan_options_layout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.scan_options_layout.setHorizontalSpacing(6)
        for (i, (label, widget)) in enumerate(img_param_widgets):    
            self.scan_options_layout.addWidget(label, i, 0, 1, 1)
            self.scan_options_layout.addWidget(widget, i, 1, 1, 1)
            
        self.scan_options.setLayout(self.scan_options_layout)

        # Spec Parameters
        self.sts_options = QGroupBox("Spectroscopy Parameters", self.options_frame)
        self.sts_options.setFlat(True)

        self.sts_mode_label = QLabel("Spectroscopy mode", self.sts_options)
        self.sts_mode = QComboBox(self.sts_options)
        self.sts_mode.addItems(["None", "Point", "Line", "Region", "All", "Pixel"])

        self.sts_initial_voltage_label = QLabel("Initial voltage", self.sts_options)
        self.sts_initial_voltage = ScientificSpinBox()
        self.sts_initial_voltage.setBounds(lower=ExponentialNumber(-5, 0), upper=ExponentialNumber(5, 0))
        self.sts_initial_voltage.setValue(ExponentialNumber(-1, 0))
        self.sts_initial_voltage.setUnits('V')

        self.sts_final_voltage_label = QLabel("Final voltage", self.sts_options)
        self.sts_final_voltage = ScientificSpinBox()
        self.sts_final_voltage.setBounds(lower=ExponentialNumber(-5, 0), upper=ExponentialNumber(5, 0))
        self.sts_final_voltage.setValue(ExponentialNumber(1, 0))
        self.sts_final_voltage.setUnits('V')

        self.sts_step_voltage_label = QLabel("Voltage increment", self.sts_options)
        self.sts_step_voltage = ScientificSpinBox()
        self.sts_step_voltage.setBounds(lower=ExponentialNumber(-5, 0), upper=ExponentialNumber(5, 0))
        self.sts_step_voltage.setValue(ExponentialNumber(25, -3))
        self.sts_step_voltage.setUnits('V')
        
        self.sts_delay_time_label = QLabel("Delay Time", self.sts_options)
        self.sts_delay_time = ScientificSpinBox()
        self.sts_delay_time.setBounds(lower=ExponentialNumber(5, -3), upper=ExponentialNumber(1, 0))
        self.sts_delay_time.setValue(ExponentialNumber(10, -3))
        self.sts_delay_time.setUnits('s')
        
        spec_param_widgets = [(self.sts_mode_label, self.sts_mode),
                             (self.sts_initial_voltage_label, self.sts_initial_voltage),
                             (self.sts_final_voltage_label, self.sts_final_voltage),
                             (self.sts_step_voltage_label, self.sts_step_voltage),
                             (self.sts_delay_time_label, self.sts_delay_time)]
        
        self.sts_options_layout = QGridLayout()
        for (i, (label, widget)) in enumerate(spec_param_widgets):    
            self.sts_options_layout.addWidget(label, i, 0, 1, 1)
            self.sts_options_layout.addWidget(widget, i, 1, 1, 1)
        self.sts_options.setLayout(self.sts_options_layout)
        self.set_enable_spectroscopy()

        # Sweep Options
        self.sweep_options = QGroupBox("Sweep Options", self.options_frame)
        self.sweep_options.setFlat(True)
        
        self.sweep_parameter_label = QLabel("Sweep parameter")
        self.sweep_parameter = QComboBox()
        self.sweep_parameter.addItems(["None", "Bias", "Size"])#, "Set point current", "Size", "X offset", "Y offset"])
        self.sweep_parameter.setCurrentText("Bias")

        self.sweep_start_label = QLabel("Initial value")
        self.sweep_start = ScientificSpinBox()
        self.sweep_start.setBounds(lower=ExponentialNumber(-5, 0), upper=ExponentialNumber(5, 0))
        self.sweep_start.setValue(ExponentialNumber(200, -3))
        self.sweep_start.setUnits('V')

        self.sweep_stop_label = QLabel("Final value")
        self.sweep_stop = ScientificSpinBox()
        self.sweep_stop.setBounds(lower=ExponentialNumber(-5, 0), upper=ExponentialNumber(5, 0))
        self.sweep_stop.setValue(ExponentialNumber(1, 0))
        self.sweep_stop.setUnits('V')

        self.sweep_step_label = QLabel("Increment")
        self.sweep_step = ScientificSpinBox()
        self.sweep_step.setBounds(lower=ExponentialNumber(-5, 0), upper=ExponentialNumber(5, 0))
        self.sweep_step.setValue(ExponentialNumber(100, -3))
        self.sweep_step.setUnits('V')

        sweep_opt_widgets = [(self.sweep_parameter_label, self.sweep_parameter),
                             (self.sweep_start_label, self.sweep_start),
                             (self.sweep_stop_label, self.sweep_stop),
                             (self.sweep_step_label, self.sweep_step)]
        
        self.sweep_options_layout = QGridLayout()
        for (i, (label, widget)) in enumerate(sweep_opt_widgets):    
            self.sweep_options_layout.addWidget(label, i, 0, 1, 1)
            self.sweep_options_layout.addWidget(widget, i, 1, 1, 1)
        self.sweep_options.setLayout(self.sweep_options_layout)

        # Spacing
        self.options_spacing = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        # Task Info
        self.total_images = QLabel("Total images:", self.options_frame)
        self.time_to_finish = QLabel("Time to finish:", self.options_frame)

        # Add task
        self.task_set_name = QLineEdit(self.options_frame, objectName="task_set_name")
        self.add_task_btn = QPushButton("Add Task Set", self.options_frame, objectName="add_task_btn")

        # Options layout
        self.options_frame_layout = QVBoxLayout(self.options_frame)
        self.options_frame_layout.setSpacing(2)
        self.options_frame_layout.setContentsMargins(0, 0, 0, 0)
        self.options_frame_layout.addWidget(self.scan_options)
        self.options_frame_layout.addWidget(self.sts_options)
        self.options_frame_layout.addWidget(self.sweep_options)
        self.options_frame_layout.addItem(self.options_spacing)
        self.options_frame_layout.addWidget(self.total_images)
        self.options_frame_layout.addWidget(self.time_to_finish)
        self.options_frame_layout.addWidget(self.task_set_name)
        self.options_frame_layout.addWidget(self.add_task_btn)

        ## Task List
        self.task_set_list = TaskSetList(title="Task Set List", objectName='task_list')
        self.task_set_list.setMinimumWidth(300)
        self.task_set_list.setMaximumWidth(525)
        
        self.content_layout = QHBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.addWidget(self.scan_area_frame)
        self.content_layout.addWidget(self.options_frame)
        self.content_layout.addWidget(self.task_set_list)
        self.content_layout.setSpacing(10)

        self.window_layout = QVBoxLayout(self.centralwidget)
        self.window_layout.addWidget(self.toolbar)
        self.window_layout.addWidget(self.content)

        self.update_total_images()
        self.update_time_to_finish()

        self.setCentralWidget(self.centralwidget)
        self.setup_events()

    def setup_events(self):
        """
            Set up event connections for various UI elements.

            This method establishes connections between different UI elements and their corresponding event-handling
            methods. It ensures that user actions trigger appropriate actions within the application.

            The following event connections are established:
            - The "Add Task Set" button and the "Return" key press in the task set name field are connected to the
            `add_task_set` method. This allows the user to add a new task set with the specified parameters.
            - The `scan_area` widget's `scan_rect_moved` signal is connected to the `scan_rect_moved` method. This signal
            is emitted when the scan area rectangle is moved, and it updates the scan area's position parameters.
            - The `scan_size` widget's `value_changed` signal is connected to the `update_scan_size` method. This signal is
            emitted when the scan size value is changed, and it updates the size of the scan area rectangle.
            - The `x_offset` and `y_offset` widgets' `value_changed` signals are connected to the `update_scan_position`
            method. These signals are emitted when the X and Y offsets are changed, respectively, and they update the
            position of the scan area rectangle.
            - Several UI elements' signals are connected to the `update_time_to_finish` method. These elements include the
            `lines_per_frame`, `line_time`, `sweep_start`, `sweep_stop`, `sweep_step`, and `repetitions` widgets. When
            any of these values are changed, the method recalculates and updates the estimated time to finish the task
            set.
            - The `sweep_parameter` widget's `currentIndexChanged` signal is connected to the `update_sweep_params`
            method. This signal is emitted when the user selects a different sweep parameter, and it updates the enabled
            status and value range of sweep-related widgets accordingly.
            - The "Play" and "Pause" toggle buttons' `clicked` signals are connected to the `play_clicked` and
            `pause_clicked` methods, respectively. These signals control the execution and pausing of task sets.
            
            Note:
                - The method `setup_events` is called during the initialization of the UI to set up event connections.
        """
        self.add_task_btn.clicked.connect(self.add_task_set)
        self.task_set_name.returnPressed.connect(self.add_task_set)
        self.scan_area.scan_rect_moved.connect(self.scan_rect_moved)
        self.scan_size.value_changed.connect(self.update_scan_size)
        
        # Scan position
        self.x_offset.value_changed.connect(self.update_scan_position)
        self.y_offset.value_changed.connect(self.update_scan_position)
        
        # Time to finish
        self.lines_per_frame.currentIndexChanged.connect(self.update_time_to_finish)
        self.line_time.value_changed.connect(self.update_time_to_finish)
        self.sweep_start.value_changed.connect(self.update_time_to_finish)
        self.sweep_stop.value_changed.connect(self.update_time_to_finish)
        self.sweep_step.value_changed.connect(self.update_time_to_finish)
        self.repetitions.valueChanged.connect(self.update_time_to_finish)

        # Total images
        self.sweep_start.value_changed.connect(self.update_total_images)
        self.sweep_stop.value_changed.connect(self.update_total_images)
        self.sweep_step.value_changed.connect(self.update_total_images)
        self.repetitions.valueChanged.connect(self.update_total_images)

        # Spectroscopy
        self.sts_mode.currentIndexChanged.connect(self.set_enable_spectroscopy)

        # Sweep param
        self.sweep_parameter.currentIndexChanged.connect(self.update_sweep_params)

        # Toolbar
        self.play.clicked.connect(self.play_clicked)
        self.pause.clicked.connect(self.pause_clicked)

    def play_clicked(self):
        """
            Handle the click event of the play button to start task execution.

            This method is triggered when the user clicks the play button on the UI. If task execution is not currently in
            progress (i.e., `running` is False), it checks if there are any task sets available for execution in the task
            list. If there are, it selects the first non-finished task set for execution and adds its tasks to the todo
            list. Then, it starts the task execution by creating and launching a TaskWorker for the first task in the todo
            list.

            Note:
                - If task execution is already in progress, clicking the play button has no effect.
                - The TaskWorker is responsible for executing individual tasks asynchronously in the background. Once a task
                is completed, the TaskWorker emits a `finished` signal, and the `restart_task_worker` method is called to
                handle the next task in the todo list or select the next task set if the current one is completed.
        """
        if self.running:
            self.play.setChecked(True)
            self.play.toggle()
        else:
            if len(self.task_set_list.task_sets) > 0:
                for task_set in self.task_set_list.task_sets:
                    if task_set.status is not TaskSetStatus.Finished:
                        self.current_task_set = task_set
                        break
                for (i, task_item) in enumerate(self.current_task_set._info.task_items):
                    if task_item.isChecked():
                        self.current_task_set.todo.append(self.current_task_set.tasks[i])
                    else:
                        task_item.setEnabled(False)
                    self.current_task_set.total_todo = len(self.current_task_set.todo)
            else:
                self.current_task_set = None
            self.start_task()

    def pause_clicked(self):
        """
            Handle the click event of the pause button to pause task execution.

            This method is triggered when the user clicks the pause button on the UI. If task execution is in progress,
            it sets the `paused` flag to True, indicating that the execution is paused. If the button is clicked again,
            the `paused` flag is set to False, and task execution resumes if there is a task set available.

            Note:
                If there are no task sets available for execution or if task execution is not currently in progress, this
                method has no effect.
        """
        if self.pause.isChecked():
            self.paused = True
        else:
            self.paused = False
            if self.running:
                if len(self.task_set_list.task_sets) > 0:
                    for task_set in self.task_set_list.task_sets:
                        if task_set.status is not TaskSetStatus.Finished:
                            self.current_task_set = task_set
                            break
                    for (i, task_item) in enumerate(self.current_task_set._info.task_items):
                        if task_item.isChecked():
                            self.current_task_set.todo.append(self.current_task_set.tasks[i])
                        else:
                            task_item.setEnabled(False)
                        self.current_task_set.total_todo = len(self.current_task_set.todo)
                else:
                    self.current_task_set = None
                self.start_task()
                
    def start_task(self):
        """
            Start the execution of the current task set.

            This method is responsible for initiating the execution of tasks within the current task set. If there are tasks
            available in the todo list of the current task set, it sets the `running` flag to True, indicating that task
            execution is in progress. It selects the first task from the todo list and creates a TaskWorker to execute it.
            The TaskWorker is then started by adding it to the thread pool.

            Once the task is completed, the TaskWorker emits a `finished` signal, and the `restart_task_worker` method is
            called to handle the next task in the todo list or select the next task set if the current one is completed.

            Note:
                - If the `running` flag is already True, calling this method has no effect, as task execution is already
                in progress.
                - The todo list contains the tasks that are yet to be executed in the current task set. Tasks are added to
                the todo list during the initialization of the task set and when a task is re-enabled for execution.
                - The `restart_task_worker` method handles the logic of selecting the next task to be executed based on the
                current state of the task set and the todo list.
        """
        if self.current_task_set is not None:
            self.current_task_set.setStatus(TaskSetStatus.Working)
            self.current_task = self.current_task_set.todo[0]
            worker = TaskWorker(self.current_task)
            worker.signals.finished.connect(self.restart_task_worker)
            self.threadpool.start(worker)
            self.running = True
        else:
            self.running = False
            self.play.setChecked(False)
            self.play.toggle()
            
    def restart_task_worker(self):
        """
            Handle the completion of a task and select the next task or task set for execution.

            This method is called when a task within the current task set is completed. It updates the status of the
            completed task and removes it from the todo list of the current task set. If there are more tasks remaining in
            the todo list, the method sets the `running` flag to True and starts the execution of the next task. If the
            current task set is not yet completed, the next task is selected from the todo list. If the current task set
            is completed, the method proceeds to select the next task set, if available, from the list of task sets.

            If there are no more tasks to be executed in the current task set and there are more task sets available, the
            method proceeds to select the next task set and the first task from its todo list for execution.

            Note:
                - The todo list contains the tasks that are yet to be executed in the current task set. Tasks are added to
                the todo list during the initialization of the task set and when a task is re-enabled for execution.
                - The method uses the `threadpool` attribute of the class to manage the execution of tasks using separate
                worker threads.
        """
        self.current_task.completed = True
        self.current_task_set._info.task_items[self.current_task.index].setEnabled(False)
        self.current_task_set.update_task_bar()
        self.current_task_set.todo.pop(0)
        
        if len(self.current_task_set.todo) == 0:
            self.current_task_set.setStatus(TaskSetStatus.Finished)
            if self.current_task_set.index < len(self.task_set_list.task_sets) - 1:
                self.current_task_set = self.task_set_list.task_sets[self.current_task_set.index + 1]                                   
                for (i, task_item) in enumerate(self.current_task_set._info.task_items):
                    if task_item.isChecked():
                        self.current_task_set.todo.append(self.current_task_set.tasks[i])
                    else:
                        task_item.setEnabled(False)
                    self.current_task_set.total_todo = len(self.current_task_set.todo)
            else:
                self.current_task_set = None

        if not self.paused:
            self.start_task()
    
    def add_task_set(self):
        """
            Add a new task set to the task list.

            This method is called when the user clicks the "Add Task Set" button or presses the "Return" key after entering
            a task set name in the corresponding QLineEdit. It creates a new TaskSetData object containing the parameters
            specified by the user for the new task set and adds it to the task list.

            Note:
                This method is responsible for extracting the values entered by the user for various task parameters,
                creating a TaskSetData object, and adding it to the task list for future execution.
        """
        sweep_param = TaskSetData.SweepParameter.none
        match self.sweep_parameter.currentText():
            case "None":
                sweep_param = TaskSetData.SweepParameter.none
            case "Bias":
                sweep_param = TaskSetData.SweepParameter.bias
            case "Size":
                sweep_param = TaskSetData.SweepParameter.size
        
        task_set_data = TaskSetData(name=self.task_set_name.text(),
                                    size=self.scan_size.value,
                                    x_offset=self.x_offset.value,
                                    y_offset=self.y_offset.value,
                                    bias=self.bias.value,
                                    set_point=self.set_point.value,
                                    line_time=self.line_time.value,
                                    lines_per_frame=int(self.lines_per_frame.currentText()),
                                    repetitions=self.repetitions.value(),
                                    sweep_parameter=sweep_param,
                                    sweep_start=self.sweep_start.value,
                                    sweep_stop=self.sweep_stop.value,
                                    sweep_step=self.sweep_step.value,
                                    total_tasks=int(self.total_images.text().split(": ")[1]),
                                    time_to_finish=self.time_to_finish.text().split(": ")[1])

        self.task_set_list.add_task_set(task_set_data)

    def update_scan_size(self):
        """
            Update the size of the scanning area based on the entered value.

            This method is triggered when the user changes the scan size value using the ScientificSpinBox widget for scan
            size. It updates the size of the scanning area (scan_rect) on the scan area display based on the entered value.

            Note:
                The scanning area size is represented as a rectangle (scan_rect) on the scan area display. This method
                updates the scan_rect size to match the value entered by the user.
        """
        newRect = self.scan_area.scan_rect.scene_inner_rect()
        newRect.setWidth(self.scan_size.value.to_float()*1e9)
        newRect.setHeight(self.scan_size.value.to_float()*1e9)
        dx = self.scan_area.scan_rect.rect().center().x() - newRect.center().x()
        dy = self.scan_area.scan_rect.rect().center().y() - newRect.center().y()
        newRect.translate(dx, dy)
        self.scan_area.scan_rect.setRect(newRect)
        self.scan_area.scan_rect.updateHandlesPos()
        self.update_time_to_finish()
        
    def update_scan_position(self):
        """
            Update the position of the scanning area based on the entered values.

            This method is triggered when the user changes the X or Y offset value using the ScientificSpinBox widgets for
            X and Y offsets. It updates the position of the scanning area (scan_rect) on the scan area display based on the
            entered X and Y offset values.

            Note:
                The scanning area (scan_rect) represents the area that will be scanned during the task execution. This
                method updates the scan_rect position to match the X and Y offset values entered by the user.
        """
        self.scan_area.scan_rect.setPos(self.x_offset.value.to_float()*1e9, self.y_offset.value.to_float()*1e9)

    def scan_rect_moved(self):
        """
            Handle the event when the scanning area (scan_rect) is moved by the user.

            This method is triggered when the user moves the scanning area (scan_rect) on the scan area display. It updates
            the X and Y offset values based on the new position of the scan_rect and the scan size based on the width of
            the scan_rect.

            Note:
                The scanning area (scan_rect) represents the area that will be scanned during the task execution. When the
                user manually moves the scan_rect, this method updates the X and Y offset values and the scan size to match
                the new position and size of the scan_rect.
        """
        scan_rect = self.scan_area.scan_rect.scene_inner_rect()
        pos = scan_rect.center()
        x = pos.x()
        y = pos.y()
        self.x_offset.setValue(ExponentialNumber(x, -9))
        self.y_offset.setValue(ExponentialNumber(y, -9))
        self.scan_size.setValue(ExponentialNumber(scan_rect.width(), -9))
        
    def update_time_to_finish(self):
        """
            Update the estimated time to finish task execution.

            This method calculates and updates the estimated time to finish task execution based on the entered values for
            various parameters, such as sweep range, line time, lines per frame, and repetitions.

            Note:
                The estimated time to finish is calculated based on the number of images to be captured during the task
                execution, the time required to capture each image (line time), and the number of repetitions for each
                task set.
        """
        N = abs((self.sweep_start.value.to_float() - self.sweep_stop.value.to_float()) // self.sweep_step.value.to_float())
        N *= self.repetitions.value()
        total_time = 2 * self.line_time.value.to_float() * float(self.lines_per_frame.currentText()) * N
        
        days = int(total_time // (24*3600))
        hours = int(total_time // (60*60)) - 24*days
        mins = int(total_time // 60) - 60*24*days - 60*hours
        secs = int(total_time) - 60*60*24*days - 60*60*hours - 60*mins
        if days > 0:
            time_to_finish = f'{days}d {hours}h {mins}m {secs}s'
        else:
            time_to_finish = f'{hours}h {mins}m {secs}s'
            
        self.time_to_finish.setText(f'Time to finish: {time_to_finish}')
        
    def update_total_images(self):
        """
            Update the total number of images to be captured.

            This method calculates and updates the total number of images to be captured during task execution based on the
            entered values for sweep parameters (start, stop, and step values) and the number of repetitions.

            Note:
                The total number of images is calculated based on the sweep range defined by the user (start, stop, and
                step values) and the number of repetitions for each task set.
        """
        N = abs((self.sweep_start.value.to_float() - self.sweep_stop.value.to_float()) // self.sweep_step.value.to_float())
        N *= self.repetitions.value()
        self.total_images.setText(f"Total images: {int(N)}")

    def set_sweep_enabled(self, value: bool):
        """
            Enable or disable sweep parameter widgets.

            This method enables or disables the widgets related to sweep parameters (start, stop, and step values) based on
            the specified value.

            Parameters:
                value (bool): True to enable the sweep parameter widgets, False to disable them.
        """
        self.sweep_start.setEnabled(value)
        self.sweep_stop.setEnabled(value)
        self.sweep_step.setEnabled(value)

    def set_sweep_units(self, units: str):
        """
            Set the units for sweep parameter widgets.

            This method sets the units for the sweep parameter widgets (start, stop, and step values) to the specified
            units.

            Parameters:
                units (str): The units to set for the sweep parameter widgets.
        """
        self.sweep_start.setUnits(units)
        self.sweep_stop.setUnits(units)
        self.sweep_step.setUnits(units)

    def set_sweep_vals(self, val: ExponentialNumber, lower: ExponentialNumber, upper: ExponentialNumber):
        """
            Set the bounds and initial value for sweep parameter widgets.

            This method sets the lower and upper bounds, as well as the initial value, for the sweep parameter widgets
            (start, stop, and step values) based on the specified values.

            Parameters:
                val (ExponentialNumber): The initial value for the sweep parameter widgets.
                lower (ExponentialNumber): The lower bound for the sweep parameter widgets.
                upper (ExponentialNumber): The upper bound for the sweep parameter widgets.
        """
        self.sweep_start.setBounds(lower, upper)
        self.sweep_start.setValue(val.copy())
        self.sweep_stop.setBounds(lower, upper)
        self.sweep_stop.setValue(val.copy())
        self.sweep_step.setBounds(lower, upper)
        self.sweep_step.setValue(val.copy())

    def update_sweep_params(self):
        """
            Update the UI based on the selected sweep parameter.

            This method is called when the user selects a different sweep parameter from the sweep parameter combo box. It
            updates the UI to reflect the selected parameter's characteristics.

            Note:
                The sweep parameter defines the parameter to be swept during the task execution. It could be "None," "Bias,"
                or "Size." Based on the selected parameter, this method enables or disables specific widgets accordingly.
        """
        sweep_param = self.sweep_parameter.currentText()
        match sweep_param:
            case "None":
                self.set_sweep_enabled(False)
                self.bias.setEnabled(True)
                self.scan_size.setEnabled(True)
            case "Bias":
                self.bias.setEnabled(False)
                self.scan_size.setEnabled(True)
                self.set_sweep_enabled(True)
                self.set_sweep_vals(self.bias.value, lower=ExponentialNumber(-5, 0), upper=ExponentialNumber(5, 0))
                self.set_sweep_units("V")
            case "Size":
                self.bias.setEnabled(True)
                self.scan_size.setEnabled(False)
                self.set_sweep_enabled(True)
                self.set_sweep_vals(self.scan_size.value, lower=ExponentialNumber(2.5, -12), upper=ExponentialNumber(3, -6))
                self.set_sweep_units("m")

    def set_enable_spectroscopy(self):
        """
            Enable or disable spectroscopy options based on the selected mode.

            This method is triggered when the user selects a different spectroscopy mode from the spectroscopy mode combo
            box. It enables or disables spectroscopy options (initial voltage, final voltage, step voltage, and delay time)
            based on the selected mode.

            Note:
                Spectroscopy allows performing measurements at different voltage points. The spectroscopy options are
                enabled or disabled depending on the selected spectroscopy mode (e.g., "Point," "Line," "Region," etc.).
        """
        match self.sts_mode.currentText():
            case 'None':
                val = False
            case _:
                val = True
        self.sts_initial_voltage.setEnabled(val)
        self.sts_final_voltage.setEnabled(val)
        self.sts_step_voltage.setEnabled(val)
        self.sts_delay_time.setEnabled(val)
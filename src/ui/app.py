from PySide6.QtCore import *
from PySide6.QtWidgets import *
from datetime import datetime

from core.exponentialnumber import ExponentialNumber
from core.tasksetdata import TaskSetData

from lib.native.taskworker import TaskWorker

from ui.native.scanarea import ScanArea
from ui.native.scientificspinbox import ScientificSpinBox
from ui.native.tasksetlist import TaskSetList
from ui.native.togglebutton import ToggleButton


class Ui_MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        ## ------ Window Settings ------ ##
        self.setWindowTitle("STM Automator")
        self.resize(1400, 800)
        self.centralwidget = QWidget(self)

        ## ------- Task threadpool ----- ##
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

        self.toolbar_layout = QHBoxLayout(self.toolbar)
        self.toolbar_layout.setSpacing(0)
        self.toolbar_layout.setContentsMargins(0, 0, 0, 0)
        self.toolbar_layout.addWidget(self.menu)
        self.toolbar_layout.addItem(self.left_space)
        self.toolbar_layout.addWidget(self.play)
        self.toolbar_layout.addWidget(self.pause)
        self.toolbar_layout.addWidget(self.stop)
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
        self.sts_mode.addItems(["None", "Point", "Line", "Region", "All"])

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

        # Sweep Options
        self.sweep_options = QGroupBox("Sweep Options", self.options_frame)
        self.sweep_options.setFlat(True)
        
        self.sweep_parameter_label = QLabel("Sweep parameter")
        self.sweep_parameter = QComboBox()
        self.sweep_parameter.addItems(["None", "Bias", "Set point current", "Size", "X offset", "Y offset"])

        self.sweep_start_label = QLabel("Start")
        self.sweep_start = ScientificSpinBox()
        self.sweep_start.setBounds(lower=ExponentialNumber(-5, 0), upper=ExponentialNumber(5, 0))
        self.sweep_start.setValue(ExponentialNumber(200, -3))
        self.sweep_start.setUnits('V')

        self.sweep_stop_label = QLabel("Stop")
        self.sweep_stop = ScientificSpinBox()
        self.sweep_stop.setBounds(lower=ExponentialNumber(-5, 0), upper=ExponentialNumber(5, 0))
        self.sweep_stop.setValue(ExponentialNumber(1, 0))
        self.sweep_stop.setUnits('V')

        self.sweep_step_label = QLabel("Step")
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
        self.add_task_btn = QPushButton("Add Task", self.options_frame, objectName="add_task_btn")

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
        self.task_set_list = TaskSetList(title="Task List", objectName='task_list')
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
        self.add_task_btn.clicked.connect(self.add_task_set)
        self.task_set_name.returnPressed.connect(self.add_task_set)
        self.scan_area.scan_rect_moved.connect(self.scan_rect_moved)
        self.scan_size.value_changed.connect(self.update_scan_size)
        self.x_offset.value_changed.connect(self.update_scan_position)
        self.y_offset.value_changed.connect(self.update_scan_position)
        self.lines_per_frame.currentIndexChanged.connect(self.update_time_to_finish)
        self.line_time.value_changed.connect(self.update_time_to_finish)
        # self.start_voltage.value_changed.connect(self.update_time_to_finish)
        # self.stop_voltage.value_changed.connect(self.update_time_to_finish)
        # self.step_voltage.value_changed.connect(self.update_time_to_finish)
        self.repetitions.valueChanged.connect(self.update_time_to_finish)
        # self.start_voltage.value_changed.connect(self.update_total_images)
        # self.stop_voltage.value_changed.connect(self.update_total_images)
        # self.step_voltage.value_changed.connect(self.update_total_images)
        self.repetitions.valueChanged.connect(self.update_total_images)

        self.play.clicked.connect(self.start_task)

    def start_task(self):
        if len(self.task_set_list.tasks) > 0:
            currentTask = self.task_set_list.tasks[0].data
            worker = TaskWorker(currentTask)
            worker.signals.finished.connect(self.restart_task_worker)
            self.threadpool.start(worker)
            
    def restart_task_worker(self):
        '''
            Update taskbar value.
            Remove task from list
        '''
        print("finished!")
                
    def add_task_set(self):
        task_set_data = TaskSetData(name=self.task_set_name.text(),
                             date=datetime.now(),
                             repetitions=self.repetitions.value(),
                             total_tasks=int(self.total_images.text().split(": ")[1]),
                             time_to_finish=self.time_to_finish.text().split(": ")[1],
                             lines_per_frame=int(self.lines_per_frame.currentText()),
                             size=self.scan_size.value,
                             set_point=self.set_point.value,
                             x_offset=self.x_offset.value,
                             y_offset=self.y_offset.value,
                             scan_speed=self.scan_speed.value,
                             line_time=self.line_time.value,
                             tasks=[])

        self.task_set_list.add_task_set(task_set_name=self.task_set_name.text(), task_set_data=task_set_data)

    def update_scan_size(self):
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
        self.scan_area.scan_rect.setPos(self.x_offset.value.to_float()*1e9, self.y_offset.value.to_float()*1e9)

    def scan_rect_moved(self):
        scan_rect = self.scan_area.scan_rect.scene_inner_rect()
        pos = scan_rect.center()
        x = pos.x()
        y = pos.y()
        self.x_offset.setValue(ExponentialNumber(x, -9))
        self.y_offset.setValue(ExponentialNumber(y, -9))
        self.scan_size.setValue(ExponentialNumber(scan_rect.width(), -9))
        
    def update_time_to_finish(self):
        # N = abs((self.start_voltage.value.to_float() - self.stop_voltage.value.to_float()) // self.step_voltage.value.to_float())
        # N *= self.repetitions.value()
        N = 1
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
        # N = abs((self.start_voltage.value.to_float() - self.stop_voltage.value.to_float()) // self.step_voltage.value.to_float())
        # N *= self.repetitions.value()
        N=1
        self.total_images.setText(f"Total images: {int(N)}")
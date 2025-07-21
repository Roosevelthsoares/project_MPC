from sklearn.calibration import CalibratedClassifierCV
from ..utils import KerasGateWrapper

class GateCalibrator:
    def __init__(self, gate_model, classes, method='isotonic'):
        self.method = method
        # self.calibrator = CalibratedClassifierCV(
        #     base_estimator=KerasGateWrapper(gate_model, classes),  # Use 'estimator' parameter
        #     cv='prefit',
        #     method=method
        # )
        self.calibrator = KerasGateWrapper(gate_model, classes)

    def calibrate(self, X_calibrate, y_calibrate):
        self.calibrator.fit(X_calibrate, y_calibrate)
        return self.calibrator
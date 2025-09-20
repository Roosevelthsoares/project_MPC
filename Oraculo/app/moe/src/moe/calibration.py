from sklearn.calibration import CalibratedClassifierCV
from ..utils import KerasGateWrapper

class GateCalibrator:
    def __init__(self, gate_model, classes, method='isotonic'):
        self.method = method
        self.calibrator = KerasGateWrapper(gate_model, classes)
        if method is not None:
            self.calibrator.fit(None, None)
            self.calibrator = CalibratedClassifierCV(
                estimator=self.calibrator,  # Use 'estimator' parameter
                cv='prefit',
                method=method
            )

    def calibrate(self, X_calibrate, y_calibrate):
        self.calibrator.fit(X_calibrate, y_calibrate)
        return self.calibrator
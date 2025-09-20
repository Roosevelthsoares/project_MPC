import logging
from sklearn.calibration import CalibratedClassifierCV
from ..utils import KerasGateWrapper

class GateCalibrator:
    def __init__(self, gate_model, classes, method='isotonic'):
        self.method = method
        self.calibrator = KerasGateWrapper(gate_model, classes)
        if method is not None:
            self.calibrator = CalibratedClassifierCV(
                base_estimator=self.calibrator,  # Use 'estimator' parameter
                cv='prefit',
                method=method
            )
        logging.info(self.calibrator.__class__.__name__)

    def calibrate(self, X_calibrate, y_calibrate):
        logging.info(X_calibrate.__class__.__name__)
        logging.info(y_calibrate.__class__.__name__)
        self.calibrator.fit(X_calibrate, y_calibrate)
        return self.calibrator
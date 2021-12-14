# Copyright © 2021 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration.  All Rights Reserved.

import requests, json
import urllib3
import pickle

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Session:
    """
    Create a new Session in `prog_server`.

    Args:
        model (str): The model to use for this session (e.g., batt)
        host (str, optional): Host address for PaaS Service. Defaults to '127.0.0.1'.
        port (int, optional): Port for PaaS Service. Defaults to 5000.
        model_cfg (dict, optional): Configuration for ProgModel.
        x0 (dict, optional): Initial state for ProgModel.
        load_est (str, optional): Load estimator to use.
        load_est_cfg (dict, optional): Configuration for load estimator.
        state_est (str, optional): State Estimator to use (e.g., ParticleFilter). Class name for state estimator in `prog_algs.state_estimators`
        state_est_cfg (dict, optional): Configuration for state estimator.
        pred (str, optional): Prediction algorithm to use (e.g., MonteCarlo). Class name for prediction algorithm in `prog_algs.predictors`
        pred_cfg (dict, optional): Configuration for prediction algorithm.

    Use:
        session = prog_client.Session(**config)
    """

    _base_url = '/api/v1'
    def __init__(self, model, host = '127.0.0.1', port=5000, **kwargs):
        self.host = 'http://' + host + ':' + str(port) + Session._base_url

        # Process kwargs with json value
        for key, value in kwargs.items():
            if isinstance(value, dict):
                kwargs[key] = json.dumps(value)
        
        # Start session
        result = requests.put(self.host + '/session', data={'model_name': model, **kwargs})
        self.session_id = json.loads(result.text)['session_id']
        self.host += "/session/" + str(self.session_id)

    def __str__(self):
        return f'PaaS Session {self.session_id}'

    def is_init(self):
        """Check if session has been initialized

        Returns:
            bool: If the session has been initialized
        """
        result = requests.get(self.host + '/initialized')
        return json.loads(result.text)['initialized']

    def send_data(self, time, **kwargs):
        """Send data to service

        Args:
            time (float): Time for data point
            ... Other arguments as keywords

        Example:
            session.send_data(10.2, t=32.0, v=3.914, i=2)
        """
        result = requests.post(self.host + '/data', data={'time': time, **kwargs})
        # TODO(CT): Check result code

    def get_state(self):
        """Get the model state 

        Returns:
            UncertainData: Model state
        """
        result = requests.get(self.host + '/state', params={'return_format': 'uncertain_data'}, stream='True')
        return pickle.load(result.raw)

    def get_predicted_state(self):
        """Get the predicted model state 

        Returns:
            list[dict]: Predicted model state at save points
        """
        result = requests.get(self.host + '/prediction/state', params={'return_format': 'uncertain_data'}, stream='True')
        return pickle.load(result.raw)

    def get_event_state(self):
        """Get the current event state

        Returns:
            dict: Event state
        """
        result = requests.get(self.host + '/event_state', params={'return_format': 'uncertain_data'}, stream='True')
        print(result.raw)
        return pickle.load(result.raw)

    def get_predicted_event_state(self):
        """Get the predicted event state

        Returns:
            list[dict]: predicted Event state
        """
        result = requests.get(self.host + '/prediction/event_state', params={'return_format': 'uncertain_data'}, stream='True')
        return pickle.load(result.raw)

    def get_predicted_toe(self):
        """Get the prediction

        Returns:
            dict: Prediction

        See also: get_prediction_status
        """
        result = requests.get(self.host + '/prediction/events', params={'return_format': 'uncertain_data'}, stream='True')
        return pickle.load(result.raw)

    def get_prediction_status(self):
        """Get the status of the prediction

        Returns:
            dict: Status of prediction 
        """
        result = requests.get(self.host + '/prediction/status')
        return json.loads(result.text)

    def get_performance_metrics(self):
        """Get current performance metrics

        Returns:
            dict: Performance Metrics
        """
        result = requests.get(self.host + '/performance_metrics', params={'return_format': 'uncertain_data'}, stream='True')
        return pickle.load(result.raw)

    def get_predicted_performance_metrics(self):
        """Get predicted performance metrics

        Args:
            return_format (str, optional): Format of returned state. Options include:
                * 'mean' (default): Return mean of state
                * 'multivariate_norm': Return mean and covariance of state
                * 'metrics': Return metrics of state

        Returns:
            list[dict]: Predicted performance Metrics
        """
        result = requests.get(self.host + '/prediction/performance_metrics', params={'return_format': 'uncertain_data'}, stream='True')
        return pickle.load(result.raw)

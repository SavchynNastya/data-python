from typing import Tuple, Optional, Dict


class SensorAnalyzer:
    def __init__(self, log_file: str):
        self.log_file = log_file

    def parse_log_line(self, line: str) -> Tuple[str, str, str, str, str]:
        """Parse a log line and extract relevant information."""
        parts = line.strip("\'").strip().split(';')
        return parts[0], parts[2].lower(), parts[6], parts[13], parts[17]

    def calculate_error_flags(self, sp1: str, sp2: str) -> str:
        """Calculate error flags based on S_P_1 and S_P_2."""
        combined = sp1[:-1] + sp2
        binary_flags = [format(int(combined[i:i+2]), '08b') for i in range(0, len(combined), 2)]
        return ''.join(flag[4] for flag in binary_flags)

    def get_error_message(self, error_flags: str) -> str:
        error_messages = {
            1: "Battery device error",
            2: "Temperature device error",
            3: "Threshold central error",
        }
        errors = [error_messages.get(index, "Unknown device error") for index, flag in enumerate(error_flags[:3], start=1) if flag == '1']
        return ", ".join(errors) if any(errors) else "Unknown device error"

    def process_sensor_logs(self) -> Tuple[Dict[str, int], Dict[str, Dict[str, Optional[str]]]]:
        """Process file to find error and success messages and count them."""
        valid_sensors: Dict[str, int] = {}
        sensor_errors: Dict[str, int] = {}
        valid_sensor_count = 0
        error_sensor_count = 0

        with open(self.log_file, 'r') as file:
            for line in file:
                if ">" in line:
                    parts = line.split(">")
                    row_data = parts[1].strip()
                    if row_data.find("BIG") != -1:
                        handler, sensor_id, sp1, sp2, state = self.parse_log_line(row_data)

                        if state == '02':  # Sensor OK
                            valid_sensors[sensor_id] = valid_sensors.get(sensor_id, 0) + 1
                            valid_sensor_count += 1
                        elif state == 'DD':  # Sensor not OK
                            sensor_errors[sensor_id] = {'count': sensor_errors.get(sensor_id, {}).get('count', 0) + 1}
                            error_sensor_count += 1
                            error_flags = self.calculate_error_flags(sp1, sp2)
                            error_message = self.get_error_message(error_flags)
                            sensor_errors[sensor_id]['error_message'] = error_message

        valid_sensors = {k: v for k, v in valid_sensors.items() if k not in sensor_errors}
        return valid_sensors, sensor_errors, sensor_errors


if __name__ == "__main__":
    logs_processor = SensorAnalyzer(log_file='C:\\Users\\Anastasia\\KPI\\Python-data\\test_tasks\\app_2.log')
    valid_sensors, sensor_errors, sensor_errors = logs_processor.process_sensor_logs()
    
    print(f"All big messages: {len(valid_sensors)+len(sensor_errors)}")
    print(f"Successful big messages: {len(valid_sensors)}")
    print(f"Failed big messages: {len(sensor_errors)}")

    print("\nSensor errors:")
    if sensor_errors:
        for sensor_id, error_details in sensor_errors.items():
            print(f"Sensor {sensor_id.upper()}: {error_details['error_message']}")
    else:
        print("No sensor errors found.")

    print("\nSuccess messages count:")
    for sensor_id, value in valid_sensors.items():
        print(f"{sensor_id.upper()}: {value}")

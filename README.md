# Mandrake API 

## Overview

This documentation outlines the endpoints, operations, and data formats supported by the API.

## Base URL

- **Base URL:** `/mandrake-api/`

API endpoints example

- `/sensors`
  
  Return collection of the sensors table.
    ```json
    [
      {
      "air_status": "test",
      "datetime": "2023-11-26T16:16:17Z",
      "humidity": 50,
      "id": 1,
      "light": 250,
      "soil": 0,
      "soil_status": "test",
      "temperature": 28
      }, ...
    ]
    ```
  
- `/sensors/sensors_data/{date}`
  * Date format **can only be** "year-month-day"
  * Example "2023-11-26"
  
  Return a history of that specific date.
    ```json
    [
      {
      "air_status": "test",
      "datetime": "2023-11-26T16:16:17Z",
      "humidity": 50,
      "id": 1,
      "light": 250,
      "soil": 0,
      "soil_status": "test",
      "temperature": 28
      }, ...
    ]
    ```
  
- `/sensors/humidity_status`

  Return latest entry of humidity and its status.

  ```json
  [
    {
    "air_status": "test",
    "humidity": 50
    }
  ]
  ```
  
- `/sensors/soil_status`

  Return latest entry of soil and its status.

  ```json
  [
    {
    "soil": 0,
    "soil_status": "string"
    }
  ]
  ```
  
- `/weather_data/forecast/{date}`
  * Date format **can only be** "year-month-day"
  * Example "2023-11-26"

  Return collection of forecast in a specific date with the latest time_get.

  ```json
  [
    {
      "cloud": 100,
      "humidity": 77,
      "id": 41,
      "main": "Rain",
      "rain": 0.19,
      "temp": 25.44,
      "time_get": "2023-11-26T06:00:05Z",
      "ts": "2023-11-26T00:00:00Z",
      "weather": "light rain"
    },
    {
      "cloud": 94,
      "humidity": 70,
      "id": 42,
      "main": "Clouds",
      "temp": 26.05,
      "time_get": "2023-11-26T06:00:05Z",
      "ts": "2023-11-26T03:00:00Z",
      "weather": "overcast clouds"
    }, ...
  ]
  ```
  
- `/weather_data/forecast/different_from_sensors`

  Return a comparison table between API data and our sensors.

  ```json
  [
    {
      "api_humidity": 69,
      "api_temp": 26.52,
      "avg_sensor_humidity": 50,
      "avg_sensor_temp": 28,
      "humidity_difference": 1.48,
      "latest_api_update": 19,
      "rounded_sensor_datetime": "2023-11-26 18:00:00",
      "temp_difference": "2023-11-26T06:00:05Z",
      "weather_data_timestamp": "2023-11-26T18:00:00Z"
    }
  ]
  ```
  


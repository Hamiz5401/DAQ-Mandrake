import sys
from flask import abort
import pymysql
from dbutils.pooled_db import PooledDB
from config import OPENAPI_STUB_DIR, DB_HOST, DB_USER, DB_PASSWD, DB_NAME

sys.path.append(OPENAPI_STUB_DIR)
from swagger_server import models

pool = PooledDB(creator=pymysql,
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWD,
                database=DB_NAME,
                maxconnections=1,
                blocking=True)


def get_sensors():
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute("SELECT * FROM sensor_data")
        result = [models.Sensors(id, datetime, soil, humidity, temperature, light, soil_status,
                                 air_status) for id, datetime, soil, humidity, temperature, light, soil_status,
                                                 air_status in cs.fetchall()]
    return result


def get_sensors_by_date(date):
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute("""
            SELECT * 
            FROM sensor_data
            WHERE datetime >= %s AND datetime <= %s
            """, (f"{date}T00:00:00.000", f"{date}T23:59:59.000"))
        result = [models.Sensors(id, datetime, soil, humidity, temperature, light, soil_status,
                                 air_status) for id, datetime, soil, humidity, temperature, light, soil_status,
                                                 air_status in cs.fetchall()]
        if not result:
            return "No sensor data on that date"
    return result


def get_humidity_status():
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute("""
            SELECT humidity, air_status 
            FROM sensor_data 
            ORDER BY datetime DESC 
            LIMIT 1
            """)
        result = [models.HumidityStatus(humidity, air_status) for humidity, air_status in cs.fetchall()]
    return result


def get_soil_status():
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute("""
            SELECT soil, soil_status 
            FROM sensor_data 
            ORDER BY datetime DESC 
            LIMIT 1
            """)
        result = [models.SoilStatus(soil, soil_status) for soil, soil_status in cs.fetchall()]
    return result


def get_forecast_by_date(date):
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute("""
            SELECT *
            FROM weather_data
            WHERE ts >= %s AND ts <= %s
                AND time_get = (
                    SELECT MAX(time_get)
                    FROM weather_data
                    WHERE ts >= %s AND ts <= %s
                    )
            """, (f"{date}T00:00:00.000", f"{date}T23:59:59.000", f"{date}T00:00:00.000", f"{date}T23:59:59.000"))
        result = [models.API(id, main, weather, temp, humidity, cloud, ts, rain, time_get)
                  for id, main, weather, temp, humidity, cloud, ts, rain, time_get in cs.fetchall()]
        if not result:
            return "No API data on that date"
    return result


def get_comparison_of_api_and_sensors():
    with pool.connection() as conn, conn.cursor() as cs:
        cs.execute("""
            SELECT
                m.rounded_sensor_datetime,
                w.ts as weather_data_timestamp,
                AVG(m.mandrake_temp) AS avg_sensor_temp,
                AVG(m.mandrake_humidity) AS avg_sensor_humidity,
                w.temp,
                w.humidity,
                w.time_get AS latest_api_update,
                ABS(ROUND(w.temp - AVG(m.mandrake_temp), 2)) AS temp_difference,
                ABS(ROUND(w.humidity - AVG(m.mandrake_humidity), 2)) AS humidity_difference
            FROM (
                SELECT
                    id AS mandrake_id,
                    CASE
                        WHEN TIME(datetime) > '21:00:00' THEN DATE_FORMAT(DATE_ADD(DATE(datetime), INTERVAL 24 HOUR), '%Y-%m-%d 00:00:00')
                        WHEN TIME(datetime) > '18:00:00' THEN DATE_FORMAT(DATE_ADD(DATE(datetime), INTERVAL 21 HOUR), '%Y-%m-%d 21:00:00')
                        WHEN TIME(datetime) > '15:00:00' THEN DATE_FORMAT(DATE_ADD(DATE(datetime), INTERVAL 18 HOUR), '%Y-%m-%d 18:00:00')
                        WHEN TIME(datetime) > '12:00:00' THEN DATE_FORMAT(DATE_ADD(DATE(datetime), INTERVAL 15 HOUR), '%Y-%m-%d 15:00:00')
                        WHEN TIME(datetime) > '09:00:00' THEN DATE_FORMAT(DATE_ADD(DATE(datetime), INTERVAL 12 HOUR), '%Y-%m-%d 12:00:00')
                        WHEN TIME(datetime) > '06:00:00' THEN DATE_FORMAT(DATE_ADD(DATE(datetime), INTERVAL 9 HOUR), '%Y-%m-%d 09:00:00')
                        WHEN TIME(datetime) > '03:00:00' THEN DATE_FORMAT(DATE_ADD(DATE(datetime), INTERVAL 6 HOUR), '%Y-%m-%d 06:00:00')
                        ELSE DATE_FORMAT(DATE_ADD(DATE(datetime), INTERVAL 3 HOUR), '%Y-%m-%d 03:00:00')
                    END AS rounded_sensor_datetime,
                    temperature AS mandrake_temp,
                    humidity AS mandrake_humidity
                FROM sensor_data
            ) m
            JOIN (
                SELECT
                    ts,
                    temp,
                    humidity,
                    time_get
                FROM weather_data w1
                WHERE time_get = (
                    SELECT MAX(time_get)
                    FROM weather_data w2
                    WHERE w1.ts = w2.ts
                )
            ) w ON m.rounded_sensor_datetime = w.ts
            GROUP BY m.rounded_sensor_datetime, w.temp, w.humidity, w.time_get
            """)
        result = [models.APIDiff(rounded_sensor_datetime, weather_data_timestamp, avg_sensor_temp,
                                 avg_sensor_humidity, api_temp, api_humidity, temp_difference, humidity_difference,
                                 latest_api_update)
                  for rounded_sensor_datetime,
                      weather_data_timestamp,
                      avg_sensor_temp,
                      avg_sensor_humidity,
                      api_temp,
                      api_humidity,
                      latest_api_update,
                      temp_difference,
                      humidity_difference
                  in cs.fetchall()]
    return result

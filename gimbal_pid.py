import time
import csv
import cv2
from robomaster import robot, vision, blaster, led

# --------------------------------------------------
# คลาสสำหรับคำนวณ PID Controller
# --------------------------------------------------
class PIDController:
    def __init__(self, kp, ki, kd, limits=(-100, 100)):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.min_limit, self.max_limit = limits
        self.last_error = 0.0
        self.integral = 0.0
        self.last_time = time.time()

    def compute(self, error):
        now = time.time()
        dt = now - self.last_time
        if dt <= 0:
            dt = 0.01

        p_term = self.kp * error
        self.integral += error * dt
        i_term = self.ki * self.integral
        derivative = (error - self.last_error) / dt
        d_term = self.kd * derivative

        output = p_term + i_term + d_term
        output = max(self.min_limit, min(self.max_limit, output))

        self.last_error = error
        self.last_time = now
        return output

    def reset(self):
        self.last_error = 0.0
        self.integral = 0.0
        self.last_time = time.time()


# PID Gains (ปรับแต่งได้ตามความเหมาะสม)
pid_yaw = PIDController(kp=120.0, ki=0.0, kd=8.0, limits=(-180, 180))
pid_pitch = PIDController(kp=100.0, ki=0.0, kd=6.0, limits=(-120, 120))

target_sequence = ["5", "1", "2"]
current_step = 0
STEP_ANGLE_YAW = 28

current_target_detected = None
is_shooting_or_moving = False

# --------------------------------------------------
# ระบบบันทึกข้อมูล Time Response (CSV)
# --------------------------------------------------
data_log = []
start_record_time = 0.0
current_pitch_angle = 0.0
current_yaw_angle = 0.0
is_firing_now = 0  # 1 เมื่อยิง, 0 เมื่ออยู่ในสภาวะปกติ

def on_gimbal_angle(angle_info):
    """Callback บันทึกมุม Pitch, Yaw จาก Gimbal (20Hz หรือ 50Hz)"""
    global current_pitch_angle, current_yaw_angle, data_log, start_record_time
    pitch_angle, yaw_angle, pitch_ground, yaw_ground = angle_info
    current_pitch_angle = pitch_angle
    current_yaw_angle = yaw_angle

    if start_record_time > 0:
        elapsed = time.time() - start_record_time
        # [Time (s), Pitch (deg), Yaw (deg), Current Target, Fired Flag]
        data_log.append([
            round(elapsed, 4),
            round(pitch_angle, 2),
            round(yaw_angle, 2),
            target_sequence[current_step],
            is_firing_now
        ])

def on_detect_marker(marker_info):
    """Callback รับพิกัดเป้าหมาย"""
    global current_target_detected, current_step, is_shooting_or_moving
    
    if is_shooting_or_moving:
        current_target_detected = None
        return

    current_target_name = target_sequence[current_step]
    found = None
    for marker in marker_info:
        x, y, w, h, info = marker
        if str(info) == current_target_name:
            found = (x, y)
            break

    current_target_detected = found


def main():
    global current_step, is_shooting_or_moving, current_target_detected
    global start_record_time, is_firing_now

    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")

    ep_gimbal = ep_robot.gimbal
    ep_blaster = ep_robot.blaster
    ep_led = ep_robot.led
    ep_vision = ep_robot.vision
    ep_camera = ep_robot.camera

    ep_led.set_led(comp=led.COMP_TOP_ALL, r=0, g=0, b=0, effect=led.EFFECT_OFF)

    print("เปิดกล้องและรีเซ็ต Gimbal...")
    ep_camera.start_video_stream(display=False)
    ep_gimbal.recenter().wait_for_completed()
    time.sleep(1)

    # เปิดรับมุมกิมบอลที่ความถี่ 20Hz (20 ครั้งต่อวินาที) สำหรับทำ Time Response
    ep_gimbal.sub_angle(freq=20, callback=on_gimbal_angle)
    start_record_time = time.time()

    print(f"เริ่มล็อกเป้าตัวแรก: หมายเลข {target_sequence[current_step]}...")
    ep_vision.sub_detect_info(name="marker", callback=on_detect_marker)

    loop_start = time.time()

    # ทำงานเป็นเวลา 60 วินาที หรือกด 'q' บนหน้าต่างภาพเพื่อจบ
    while time.time() - loop_start < 20:
        img = ep_camera.read_cv2_image(strategy="newest", timeout=0.5)
        if img is not None:
            cv2.putText(
                img,
                f"Target: {target_sequence[current_step]} | Yaw: {current_yaw_angle:.1f}",
                (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )
            cv2.imshow("RoboMaster Time Response Recording", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        if is_shooting_or_moving:
            continue

        if current_target_detected is not None:
            x, y = current_target_detected
            err_x = x - 0.5
            err_y = 0.5 - y

            # ล็อกเป้าเข้ากลางจอ (Error < 3%)
            if abs(err_x) < 0.03 and abs(err_y) < 0.03:
                is_shooting_or_moving = True
                ep_gimbal.drive_speed(pitch_speed=0, yaw_speed=0)
                
                print(f">> [HIT] ล็อกและยิงเป้า {target_sequence[current_step]} เรียบร้อย!")
                is_firing_now = 1  # มาร์กจุดในกราฟว่าเกิดการยิงที่วินาทีนี้

                # เปิดไฟ LED สีแดงและยิง IR
                ep_led.set_led(comp=led.COMP_TOP_ALL, r=255, g=0, b=0, effect=led.EFFECT_ON)
                ep_blaster.fire(fire_type=blaster.INFRARED_FIRE, times=1)
                time.sleep(0.15)
                ep_led.set_led(comp=led.COMP_TOP_ALL, r=0, g=0, b=0, effect=led.EFFECT_OFF)

                is_firing_now = 0
                pid_yaw.reset()
                pid_pitch.reset()

                # หันกิมบอลไปยังทิศทางเป้าถัดไป
                if current_step == 0:
                    print(f">> หันขวา ครั้งที่ 1 (+{STEP_ANGLE_YAW} องศา) ไปหาเป้า 1")
                    ep_gimbal.move(pitch=0, yaw=STEP_ANGLE_YAW, pitch_speed=60, yaw_speed=60).wait_for_completed()
                    current_step = 1
                elif current_step == 1:
                    print(f">> หันขวา ครั้งที่ 2 (+{STEP_ANGLE_YAW} องศา) ไปหาเป้า 2")
                    ep_gimbal.move(pitch=0, yaw=STEP_ANGLE_YAW, pitch_speed=60, yaw_speed=60).wait_for_completed()
                    current_step = 2
                elif current_step == 2:
                    return_yaw = -(STEP_ANGLE_YAW * 2)
                    print(f">> ยิงครบ 3 เป้า! หันซ้ายชดเชย ({return_yaw} องศา) กลับไปเป้า 5")
                    ep_gimbal.move(pitch=0, yaw=return_yaw, pitch_speed=80, yaw_speed=80).wait_for_completed()
                    current_step = 0

                time.sleep(0.3)
                is_shooting_or_moving = False
            else:
                yaw_speed = pid_yaw.compute(err_x)
                pitch_speed = pid_pitch.compute(err_y)
                ep_gimbal.drive_speed(pitch_speed=pitch_speed, yaw_speed=yaw_speed)
        else:
            ep_gimbal.drive_speed(pitch_speed=0, yaw_speed=0)

    # ยกเลิก Subscription และปิดระบบ
    ep_gimbal.unsub_angle()
    ep_vision.unsub_detect_info(name="marker")
    ep_camera.stop_video_stream()
    cv2.destroyAllWindows()
    ep_led.set_led(comp=led.COMP_ALL, r=0, g=0, b=0, effect=led.EFFECT_OFF)
    ep_robot.close()

    # บันทึกข้อมูลทั้งหมดลงไฟล์ CSV
    csv_filename = "gimbal_response.csv"
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["time_sec", "pitch_angle", "yaw_angle", "target", "is_fired"])
        writer.writerows(data_log)

    print(f"\n>> บันทึกข้อมูล Time Response เรียบร้อยแล้ว: {csv_filename} (ทั้งหมด {len(data_log)} แถว)")


if __name__ == '__main__':
    main()
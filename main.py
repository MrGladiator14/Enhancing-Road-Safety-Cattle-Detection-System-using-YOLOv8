import cv2
import argparse
import time
from ultralytics import YOLO
import supervision as sv
import numpy as np
from sendmail import sendmail 


ZONE_POLYGON = np.array([
    [0, 0],
    [0.5, 0],
    [0.75, 1],
    [0, 1]
])


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="YOLOv8 live")
    parser.add_argument(
        "--webcam-resolution", 
        default=[1280, 720], 
        nargs=2, 
        type=int
    )
    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()
    frame_width, frame_height = args.webcam_resolution
    IP = 'http://192.168.192.20:8080/video'
    cap = cv2.VideoCapture(IP)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        exit()
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

    model = YOLO("yolov8l.pt")

    box_annotator = sv.BoxAnnotator(
        thickness=2,
        text_thickness=2,
        text_scale=1
    )

    zone_polygon = (ZONE_POLYGON * np.array(args.webcam_resolution)).astype(int)
    zone = sv.PolygonZone(polygon=zone_polygon, frame_resolution_wh=tuple(args.webcam_resolution))
    zone_annotator = sv.PolygonZoneAnnotator(
        zone=zone, 
        color=sv.Color.red(),
        thickness=2,
        text_thickness=4,
        text_scale=2
    )
    start_time = None

    while True:
        ret, frame = cap.read()

        result = model(frame, agnostic_nms=True)[0]
        detections = sv.Detections.from_yolov8(result)
        detections = detections[detections.class_id == 19]
        labels = [
            f"cattle {confidence:0.2f}"
            for _, confidence, class_id, _
            in detections
        ]
        frame = box_annotator.annotate(
            scene=frame, 
            detections=detections, 
            labels=labels
        )

        zone.trigger(detections=detections)
        frame = zone_annotator.annotate(scene=frame)      
        count_in_zone = len(detections)
        if count_in_zone >0 and start_time is None:
            start_time = time.time()

        if count_in_zone == 0 and start_time is not None:
            end_time = time.time()
            elapsed_time = (end_time - start_time)
            print("Count reached 0. Elapsed time:", elapsed_time, "seconds")
            start_time = None
        n = time.time()
        if start_time is not None and ((n - start_time) > 5):
            sendmail(IP)
            start_time = None

        print(count_in_zone)
        cv2.imshow("yolov8", frame)


        if (cv2.waitKey(30) == 27):
            break


if __name__ == "__main__":
    main()
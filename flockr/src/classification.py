import numpy as np
import cv2
from PIL import Image, ImageOps
import sqlite3
import time
from tflite_support.task import core
from tflite_support.task import processor
from tflite_support.task import vision
from camera import start_camera, get_latest_frame

THRESHOLD = 0.7
NAMEDBPATH = "birdnames.db"

should_ff = True
should_rw = False
last_bird_seen = None

# Initialize the image classification model
base_options = core.BaseOptions(
    file_name="model.tflite", use_coral=False, num_threads=4
)

# Enable Coral by this setting
classification_options = processor.ClassificationOptions(
    max_results=1, score_threshold=0
)
options = vision.ImageClassifierOptions(
    base_options=base_options, classification_options=classification_options
)

# create classifier
global classifier
classifier = vision.ImageClassifier.create_from_options(options)


def load_labels_from_db():
    conn = sqlite3.connect(NAMEDBPATH)
    cursor = conn.cursor()

    # Assuming table is named 'labels' and column is 'name'
    cursor.execute("SELECT common_name FROM birdnames;")
    labels = [row[0] for row in cursor.fetchall()]

    conn.close()
    return labels


def classify(np_array):
    tensor_image = vision.TensorImage.create_from_array(np_array)
    categories = classifier.classify(tensor_image)
    return categories.classifications[0].categories


def format_frame(frame):
    # Resize as per model requirement
    image = Image.fromarray(frame)
    max_size = (224, 224)
    image.thumbnail(max_size)

    # Pad the image to fill the remaining space
    padded_image = ImageOps.expand(
        image,
        border=((max_size[0] - image.size[0]) // 2, (max_size[1] - image.size[1]) // 2),
        fill="black",
    )  # Change the fill color if necessary

    np_image = np.array(padded_image)
    return np_image


def get_common_name(scientific_name):
    conn = sqlite3.connect(NAMEDBPATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT common_name FROM birdnames WHERE scientific_name = ?",
        (scientific_name,),
    )
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]
    else:
        print("No common name for: " + scientific_name, flush=True)
        return "No common name found."


def fast_forward():
    global should_ff
    should_ff = True


def rewind():
    global should_rw
    should_rw = True


def generate_frames(is_live, socketio):
    global should_ff
    global should_rw
    global last_bird_seen

    if is_live:
        start_camera()
        fps = 10  # approximate, adjust if needed
        frame_interval = 10  # process every 10th frame
        frame_count = 0

        while True:
            frame = get_latest_frame()
            if frame is None:
                time.sleep(0.05)
                continue

            start_time = time.time()
            _, buffer = cv2.imencode(".jpg", frame)

            if frame_count % frame_interval == 0:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                np_image = format_frame(frame_rgb)
                categories = classify(np_image)
                category = categories[0]
                index = category.index
                score = category.score
                display_name = category.display_name

                if index != 964 and score > THRESHOLD:
                    common_name = get_common_name(display_name)
                    if common_name != last_bird_seen:
                        last_bird_seen = common_name
                    result_text = [f"Label: {common_name} Score: {score}"]
                    print(f"Live Inference: {result_text}")
                    socketio.emit("result", {"label": common_name, "score": score})

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
            )
            elapsed_time = time.time() - start_time
            time.sleep(max(1.0 / fps - elapsed_time, 0))
            frame_count += 1

    else:
        cap = cv2.VideoCapture("test-video.mp4")
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(fps)
        frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("End of video.")
                break

            if should_ff:
                current_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
                cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame + (10 * frame_interval))
                should_ff = False

            if should_rw:
                current_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
                cap.set(
                    cv2.CAP_PROP_POS_FRAMES,
                    max(0, current_frame - (10 * frame_interval)),
                )
                should_rw = False

            start_time = time.time()
            _, buffer = cv2.imencode(".jpg", frame)

            if frame_count % frame_interval == 0:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                np_image = format_frame(frame_rgb)
                categories = classify(np_image)
                category = categories[0]
                index = category.index
                score = category.score
                display_name = category.display_name

                if index != 964 and score > THRESHOLD:
                    timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
                    common_name = get_common_name(display_name)
                    if common_name != last_bird_seen:
                        last_bird_seen = common_name
                    result_text = [f"Label: {common_name} Score: {score}"]
                    print(f"Demo Timestamp: {timestamp} seconds, {result_text}")
                    socketio.emit("result", {"label": common_name, "score": score})

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
            )
            elapsed_time = time.time() - start_time
            time.sleep(max(1.0 / fps - elapsed_time, 0))
            frame_count += 1

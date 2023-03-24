
import cv2
import face_recognition
import os
import glob
from django.http import JsonResponse, HttpResponse ,StreamingHttpResponse
from PIL import Image
import json
import base64


def capture_and_save_image(request):
    # Access the default camera device
    cap = cv2.VideoCapture(0)

    # Create a window to display the camera feed
    cv2.namedWindow("Capture Image")

    # Initialize the filename variable
    filename = None

    # Capture images until the user presses "s" to save the image
    while True:
        # Capture an image
        ret, frame = cap.read()

        # Show the image in the window
        cv2.imshow("Capture Image", frame)

        # Wait for the user to press a key
        key = cv2.waitKey(1)

        # If the user presses "s", prompt for the filename and save the image
        if key == ord('s'):
            
            # Prompt the user to enter a filename without extension
            filename_without_ext = input("Enter filename: ")

            if not filename_without_ext:
                return JsonResponse({'status': 'error', 'message': 'Filename not provided'})

            # Check if the filename has an extension
            if '.' in filename_without_ext:
                return JsonResponse({'status': 'error', 'message': 'Filename should not include extension'})

            # Add the ".jpeg" extension to the filename
            filename = f"{filename_without_ext}.jpeg"

            # Save the image in the "faces" folder
            path = os.path.join(os.getcwd(), 'faces', filename)
            image = Image.fromarray(frame)
            image.save(path)


        # If the user presses the "q" key, exit the loop
        if key == ord('q'):
            cv2.destroyAllWindows()
            break

    # Release the camera device
    cap.release()

    # Return a response with the filename
    if filename:
        return JsonResponse({'status': 'success', 'filename': filename})
    else:
        return JsonResponse({'status': 'error', 'message': 'Image not captured'})
  
#############################

def generate_frames():
    # Load known faces from folder
    known_faces = []
    known_labels = []
    for filename in glob.glob('faces/*.*'):
        # Load face image and extract label from filename
        image = face_recognition.load_image_file(filename)
        label = os.path.splitext(os.path.basename(filename))[0]

        # Append face image and label to lists
        known_faces.append(image)
        known_labels.append(label)

    # Encode known faces
    known_encodings = [face_recognition.face_encodings(face)[0] for face in known_faces]

    # Start video capture from camera
    cap = cv2.VideoCapture(0)

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Find all faces in the frame
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        # Recognize each face
        for face_encoding, face_location in zip(face_encodings, face_locations):
            # Compare face encoding with known encodings
            matches = face_recognition.compare_faces(known_encodings, face_encoding)

            # Find best match
            match_index = matches.index(True) if True in matches else -1

            top, right, bottom, left = face_location
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            # Print name of recognized face
            if match_index >= 0:
                name = known_labels[match_index]
                print(name)
            else:
                name = 'unknown'
                print(name)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            # Encode the frame as JPEG image
            _, jpeg_frame = cv2.imencode('.jpg', frame)
            jpeg_bytes = jpeg_frame.tobytes()

            # Yield JPEG-encoded frame
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg_bytes + b'\r\n')

    # Release video capture and close window
    cap.release()
    cv2.destroyAllWindows()

def face_recognition_api(request):
    return StreamingHttpResponse(generate_frames(), content_type='multipart/x-mixed-replace; boundary=frame')


        
# ##################################

    

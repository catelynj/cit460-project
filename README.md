# Smart Glasses
*CIT 460: Advanced Topics in Programming*
### Description:
The goal of the Smart Glasses project is to have an attachment for glasses that allows the user to detect and interact with text visible to the attached camera. The attachment will include a camera that will utilize OpenCV's EAST model to detect visible text and PyTesseract, an OCR engine, to analyze it. With that text, the user can prompt the application through spoken action words after pressing the prompt sensor on the attachment. Given a prompt, the application will choose the appropriate API to use, such as Wolfram|Alpha or Google Translate. All API responses will either be played to the user through a connected audio device or available as a text response in the companion app. The secondary function of the attachment will be to take photos and videos that the user can save, view, and download through the mobile application.

### Project Plan: 
Sprint 1 (February 3rd to March 1st):
 
-	Raspberry Pi:\
o	Load OS\
o	Attach Camera\
o	Attach Battery Pack\
o	Attach Touch Sensor\
o	Create Housing
-	Main Application:\
o	Setup Development Environment\
o	Download Packages\
o	Ensure Compatibility\
o	API Responses
 
Sprint 2 (March 2nd – March 29th):
 
-	Main Application:\
o	Bluetooth Connectivity\
o	Text Detection\
o	OCR\
o	Prompt API w/ OCR Input\
o	Action Word Prompting

Sprint 3 (March 30th – April 26th)
 
-	Companion Application:\
o	Setup Emulator\
o	Connect to Main Application\
o	Display API Responses\
o	Store Images & Videos / Download Images & Videos\
o	Design UI


### Operational Theory
The device operates through a capacitive touch sensor that serves as the primary input, interpreting single and multi-touch gestures to trigger functions. A single touch activates the prompt pipeline, which routes the input based on keyword detection — queries containing "Ask" or "Question" are forwarded to the Wolfram|Alpha API for computational responses, while translation requests are handled by the OCR pipeline. Two touches trigger the camera to capture an image, which is then saved locally. Three touches initiate video recording, and a subsequent three-touch input signals the device to stop recording, also initially saved locally. Finally, all media and API queries are cached and sent to the mobile companion app using FastAPI endpoints on an uvicorn server.
<img width="550" height="340" alt="Operational Theory Decision Tree" src="https://github.com/user-attachments/assets/e20f8dda-5b59-46fb-9a3e-bf7737596146" />

### Functional Theory
The smart glasses system is built around four main functionalities. Actions are handled through a touch sensor for input, a PiCamera for image capture, and PyTTS for text-to-speech output. Prompt processing is powered by the Wolfram|Alpha API for computational queries and Google Speech Recognition (SR) for voice input. Text translation leverages the Translators library alongside an OpenCV EAST model and Tesseract for OCR-based text detection and recognition. Finally, a companion app built with Flutter provides the frontend interface, backed by a FastAPI/uvicorn server and SQLite database for data management and communication.

### Algorithms
The system relies on three core algorithmic components. A touch input state machine tracks touch counts and implements a timeout mechanism to avoid false positives, along with a press-wait delay to prevent touches from being cut off prematurely. For text detection and recognition, the OpenCV EAST model uses a Fully Convolutional Neural Network (FCN) for deep-learning-based text detection, which is then paired with Tesseract's OCR engine, using a Recurrent Neural Network (RNN), to extract and interpret the detected text. Finally, a prompt history cache is maintained via an SQLite table that stores each query and its corresponding answer, exposed through a FastAPI endpoint so the companion app can retrieve prompt history on load.

### Impact
This project has the potential to make a meaningful contribution to the IT world across three key areas. The first is modularity, the codebase is intentionally structured with clear function separation, making it straightforward to extend and build upon. This was best illustrated when my professor suggested merging two of my earlier concepts, basic smart glasses with computer vision capabilities and a Pokémon card identification app. Thanks to the abstracted architecture, adding such an extension, whether for card scanning, price checking, or similar features, requires minimal effort and fits naturally into the existing framework.

The second area is the growing "low-tech high-tech" movement, popularized in part by online communities building retro-inspired devices called cyberdecks. This project embodies that philosophy, the hardware is intentionally minimal and accessible, yet the functionality is genuinely sophisticated. The design scales easily with better components, but its greatest strength is replicability. Anyone with entry-level hardware can build a working version, lowering the barrier for exploration and innovation.

Finally, this project contributes to market diversity in the smart glasses space. While it is not positioned to compete directly with consumer products like Meta Ray-Bans, it serves as a viable proof of concept demonstrating that capable, wearable assistive technology can be built affordably and openly. With further refinement, this architecture could form the foundation for a lower-cost alternative to the current smart glasses solutions.

### Security
The reliance on external APIs such as Wolfram|Alpha and Google Speech Recognition introduces exposure to third-party availability and data handling practices. Malicious input, whether through crafted voice prompts or injected text via the OCR pipeline, poses a risk if left unvalidated. Additionally, the project's dependence on open-source packages creates potential vulnerabilities if those packages are compromised or unmaintained.

To address these concerns, several solutions are currently in place. Input sanitization is applied to clean and validate data before it is passed through any processing. Any data being returned by external APIs is not being executed, simply displayed to the user as plain-text or as TTS. All external libraries and APIs were selected from reputable, well-maintained sources to minimize the risk of supply chain issues. Finally, package pinning is used to lock dependencies to specific versions, preventing unexpected behavior from updates and ensuring a consistent, safe build environment.

### Integration
Deploying a wearable device with a camera and a microphone naturally raises a number of ethical and practical considerations. On the ethical side, consent is a primary concern. Bystanders being recorded or having their text captured may be unaware the device is in use, which warrants clear usage guidelines and responsible usage practices. In its current state, this attachment is incredibly visible, so this concern is mitigated to a certain extent. There is also an important distinction between the use of AI versus APIs in this project. Rather than relying on a generative AI model making inferences and possibly hallucinating, the system utilizes a deterministic, computational API, Wolfram|Alpha, which provides factual responses when information is available. This distinction matters ethically because the system's behavior is more transparent, predictable, and auditable than a black-box AI model.

On the practical side, real-time performance remains an ongoing challenge, as latency from API calls, OCR processing, and TTS output can vary depending on network conditions and hardware limitations. Additionally, as time progresses, the current hardware stack will become increasingly outdated and have more performance issues. This can be combatted with improved hardware and corrective maintenance (software/package updates, optimizations, etc.).

### Outcome
_Flutter Companion App_
| API Chat History | Media Gallery |
| ------------- | ------------- |
| <img width="219" height="488" alt="Flutter App Chat History" src="https://github.com/user-attachments/assets/efe8d023-568b-4d1a-b7e5-768a110da397" />  | <img width="219" height="488" alt="Flutter App Media Gallery" src="https://github.com/user-attachments/assets/1c223b5d-9376-414d-a70a-62a68831bfbf" /> |

_Text Translation with EAST & Tesseract_
| Text Translation | Image Used |
| ------------- | ------------- |
|<img width="511" height="200" alt="Screenshot 2026-05-05 220222" src="https://github.com/user-attachments/assets/e76e936f-cead-4088-9947-523df62a58c5" /> |<img width="695" height="147" alt="card" src="https://github.com/user-attachments/assets/29a2d366-2903-4a57-b241-5197db18f18d" />|


 
 




### References:
_Debugging and headaches dealt with using Claude_ 
- Emmer, C. (2024, March 7). Quickly Pin Python Package Versions | Christian Emmer. Christian Emmer. https://emmer.dev/blog/quickly-pin-python-package-versions/FastAPI. (n.d.). 
- Fastapi.tiangolo.com. https://fastapi.tiangolo.com/#installation
- Flutter. (2024). Flutter documentation. Docs.flutter.dev. https://docs.flutter.dev/
- maker_soupRead. (n.d.). How to Make Smart Glasses! Instructables. https://www.instructables.com/Smart-Glasses-V2/
- moukthika. (2025, March 17). Text Detection and Removal using OpenCV. OpenCV. https://opencv.org/blog/text-detection-and-removal-using-opencv/
- Raspberry Pi Documentation. (2026). Raspberrypi.com. https://www.raspberrypi.com/documentation/#powerReps
- Rosebrock, A. (2018, September 17). OpenCV OCR and text recognition with Tesseract. PyImageSearch. https://pyimagesearch.com/2018/09/17/opencv-ocr-and-text-recognition-with-tesseract/
- The Picamera2 Library A libcamera-based Python library for Raspberry Pi cameras. (n.d.). Retrieved May 4, 2026, from https://pip-assets.raspberrypi.com/categories/652-raspberry-pi-camera-module-2/documents/RP-008156-DS-2-picamera2-manual.pdf
- Uberi. (n.d.). speech_recognition/examples/microphone_recognition.py at master · Uberi/speech_recognition. GitHub. https://github.com/Uberi/speech_recognition/blob/master/examples/microphone_recognition.py
- Wolfram|Alpha Short Answers API: Reference & Documentation. (2026). Wolframalpha.com.   https://products.wolframalpha.com/short-answers-api/documentation




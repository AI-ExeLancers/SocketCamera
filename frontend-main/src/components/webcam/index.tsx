// import React, { useRef, useEffect, useState } from 'react';
// import Webcam from 'react-webcam';
// import useWebSocket from 'react-use-websocket';

// interface WebSocketMessage {
//     processedFrame: string;
//     faceDetected: boolean;
// }

// const WebCam: React.FC = () => {
//     const webcamSenderRef = useRef<Webcam>(null);
//     const [receivedFrame, setReceivedFrame] = useState<string | null>(null);

//     const { sendJsonMessage, lastJsonMessage } = useWebSocket<WebSocketMessage>('ws://127.0.0.1:8000/ws/facedetection/', {
//         onOpen: () => console.log('WebSocket connection established.'),
//         onClose: () => console.log('WebSocket connection closed.'),
//         shouldReconnect: () => true,
//     });

//     const captureFrame = () => {
//         if (webcamSenderRef.current) {
//             const imageSrc = webcamSenderRef.current.getScreenshot();
//             if (imageSrc) {
//                 sendJsonMessage({ frame: imageSrc });
//             }
//         }
//     };

//     useEffect(() => {
//         const interval = window.setInterval(captureFrame, 1000 / 30); // 30 FPS
//         return () => {
//             window.clearInterval(interval);
//         };
//     }, []);

//     useEffect(() => {
//         if (lastJsonMessage && lastJsonMessage.processedFrame) {
//             setReceivedFrame(lastJsonMessage.processedFrame);
//         }
//     }, [lastJsonMessage]);

//     return (
//         <div className='container'>
//             <div className="row">
//                 <div className="col-xl-6">
//                     <Webcam
//                         height={600}
//                         width={600}
//                         ref={webcamSenderRef}
//                         screenshotFormat="image/jpeg"
//                         screenshotQuality={0.8}
//                         className="webcam"
//                     />
//                 </div>
//                 <div className="col-xl-6">
//                     {receivedFrame ? (
//                         <img src={receivedFrame} alt="Received Frame" height={600} width={600} className="webcam" />
//                     ) : (
//                         <div style={{ height: 600, width: 600, backgroundColor: 'black' }} />
//                     )}
//                 </div>
//             </div>
//         </div>
//     );
// };

// export default WebCam;





// import React, { useRef, useEffect, useState } from 'react';
// import Webcam from 'react-webcam';

// const WebCam: React.FC = () => {
//     const webcamSenderRef = useRef<Webcam>(null);
//     const [receivedFrame, setReceivedFrame] = useState<string | null>(null);
//     const intervalRef = useRef<number | null>(null);

//     const captureFrame = () => {
//         if (webcamSenderRef.current) {
//             const imageSrc = webcamSenderRef.current.getScreenshot();
//             if (imageSrc) {
//                 sendFrameToBackend(imageSrc);
//             }
//         }
//     };

//     const sendFrameToBackend = async (frame: string) => {
//         try {
//             const response = await fetch('http://127.0.0.1:8000/process_frames', {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json',
//                 },
//                 body: JSON.stringify({ frame }),
//             });
//             const data = await response.json();
//             console.log("data",data)
//             if (data && data.processedFrame) {
//                 setReceivedFrame(data.processedFrame);
//             }
//         } catch (error) {
//             console.error('Error sending frame to backend:', error);
//         }
//     };

//     useEffect(() => {
//         intervalRef.current = window.setInterval(captureFrame, 1000 / 30); // 30 FPS
//         return () => {
//             if (intervalRef.current) {
//                 window.clearInterval(intervalRef.current);
//             }
//         };
//     }, []);

//     return (
//         <div className='container'>
//             <div className="row">
//                 <div className="col-xl-6">
//                     <Webcam
//                         height={600}
//                         width={600}
//                         ref={webcamSenderRef}
//                         screenshotFormat="image/jpeg"
//                         screenshotQuality={0.8}
//                         className="webcam"
//                     />
//                 </div>
//                 <div className="col-xl-6">
//                     {receivedFrame ? (
//                         <img src={receivedFrame} alt="Received Frame" height={600} width={600} className="webcam" />
//                     ) : (
//                         <div style={{ height: 600, width: 600, backgroundColor: 'black' }} />
//                     )}
//                 </div>
//             </div>
//         </div>
//     );
// }

// export default WebCam;
import React, { useRef, useEffect, useState } from 'react';
import Webcam from 'react-webcam';

const mimeType = "video/webm";

const WebCam = () => {
    const webcamSenderRef = useRef<Webcam>(null);
    const [receivedFrame, setReceivedFrame] = useState<string | null>(null);
    const intervalRef = useRef<number | null>(null);
    const [recordingStatus, setRecordingStatus] = useState("inactive");
    const [recordedVideo, setRecordedVideo] = useState<string | null>(null);
    const mediaRecorder = useRef<MediaRecorder | null>(null);
    const [frameCount, setFrameCount] = useState(0);
    const [lastFrame, setLastFrame] = useState<string | null>(null);
    const [videoChunks, setVideoChunks] = useState<Blob[]>([]);

    const captureFrame = () => {
        if (webcamSenderRef.current) {
            const imageSrc = webcamSenderRef.current.getScreenshot();
            if (imageSrc) {
                sendFrameToBackend(imageSrc);
                setLastFrame(imageSrc); // Store the last captured frame
            }
        }
    };

    const sendFrameToBackend = async (frame: string) => {
        try {
            const response = await fetch('http://127.0.0.1:8000/process_frames', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ frame }),
            });
            const data = await response.json();
            console.log("data", data);
            if (data && data.frames) {
                setReceivedFrame(data.frames);
            }
        } catch (error) {
            console.error('Error sending frame to backend:', error);
        }
    };

    const startRecording = () => {
        setFrameCount(0);
        setRecordingStatus("recording");
        setVideoChunks([]);
        
        if (!intervalRef.current) {
            intervalRef.current = window.setInterval(captureFrame, 1000 / 30); // 30 FPS
        }

        const stream = webcamSenderRef.current?.video?.srcObject as MediaStream;
        const media = new MediaRecorder(stream, { mimeType });
        mediaRecorder.current = media;

        mediaRecorder.current.ondataavailable = (event) => {
            if (event.data.size > 0) {
                setVideoChunks(prev => [...prev, event.data]);
            }
        };

        mediaRecorder.current.start();
    };

    const stopRecording = async () => {
        setRecordingStatus("inactive");
        if (intervalRef.current) {
            window.clearInterval(intervalRef.current);
            intervalRef.current = null;
        }

        if (mediaRecorder.current) {
            mediaRecorder.current.stop();
            mediaRecorder.current.onstop = () => {
                const videoBlob = new Blob(videoChunks, { type: mimeType });
                const videoUrl = URL.createObjectURL(videoBlob);
                setRecordedVideo(videoUrl);
            };
        }

        // Send the last captured frame to the finalize_video endpoint
        if (lastFrame) {
            try {
                await fetch('http://127.0.0.1:8000/finalize_video', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ image: lastFrame }), // Send the last captured frame
                });
            } catch (error) {
                console.error('Error sending last frame to finalize_video endpoint:', error);
            }
        }
    };

    useEffect(() => {
        return () => {
            stopRecording();
        };
    }, []);

    return (
        <div className='container'>
            <div className="row">
                <div className="col-xl-6">
                    <Webcam
                        height={600}
                        width={600}
                        ref={webcamSenderRef}
                        screenshotFormat="image/jpeg"
                        screenshotQuality={0.8}
                        className="webcam"
                    />
                </div>
                <div className="col-xl-6">
                    {receivedFrame ? (
                        <img src={receivedFrame} alt="Received Frame" height={600} width={600} className="webcam" />
                    ) : (
                        <div style={{ height: 600, width: 600, backgroundColor: 'black' }} />
                    )}
                </div>
            </div>
            <div className="row">
                <div className="col">
                    <button onClick={startRecording} className="btn btn-primary">Start Recording</button>
                    <button onClick={stopRecording} className="btn btn-secondary">Stop Recording</button>
                </div>
            </div>
            {/* {recordedVideo && (
                <div className="row">
                    <div className="col">
                        <h3>Recorded Video</h3>
                        <video style={{ height: '300px' }} controls src={recordedVideo}></video>
                    </div>
                </div>
            )} */}
        </div>
    );
};

export default WebCam;

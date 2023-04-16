
using System.Collections;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.Networking;
using UnityEngine.UI;
using TMPro;
using LitJson;
using System.Collections.Generic;
using System;
/// <summary>
/// This class is used to connect to a server and send a request to get a stream of audio data. 
/// It will automatically start recording when the audio level is above a threshold and stop recording when the audio level is below a threshold.
/// </summary>
public class ServerConnectionStreamAuto : MonoBehaviour
{
    #region Editor Exposed Variables

    /// <summary>
    /// The host to post the audio file to
    /// </summary>
    [Tooltip("The host to post the audio file to")]
    public string host = "localhost";
    /// <summary>
    /// The port to post the audio file to
    /// </summary>
    [Tooltip("The port to post the audio file to")]
    public string port = "8080";
    /// <summary>
    /// The path to post the audio file to
    /// </summary>
    [Tooltip("The path to post the audio file to")]
    public string path = "audio_converse_stream";
    /// <summary>
    /// The sender id for rasa to use
    /// </summary>
    [Tooltip("The sender id for rasa to use")]
    public string sender_id = "Unity";
    /// <summary>
    /// The bot to use
    /// </summary>
    [Tooltip("Bot to use")]
    public string bot;
    /// <summary>
    /// Use SSL or not
    /// </summary>
    [Tooltip("Use SSL or not")]
    public bool ssl = false;
    /// <summary>
    /// input audio sample rate
    /// <summary>
    [Tooltip("input audio sample rate")]
    public int inputSampleRate = 44100;
    /// <summary>
    /// output audio sample rate
    /// <summary>
    [Tooltip("output audio sample rate")]
    public int outputSampleRate = 16000;

    /// <summary>
    /// Set the outputsource
    /// <summary>
    [Tooltip("audiosource from where to play the response")]
    public AudioSource outputSource;

    /// <summary>
    /// Set the playback of processing sound
    /// <summary>
    [Tooltip("Set the playback of processing sound when input is detected")]
    public AudioSource processingSource;
    /// <summary>
    /// autostart recording when the scene is loaded without pressing the button
    /// </summary>
    public bool autoStart = false;
    /// <summary>
    /// Set the audiosource threshold noise level before starting recording
    /// <summary>
    [Tooltip("Sound noise level threshold before starting recording")]
    public double audioLevelUpperThreshold = 0.03;
    /// <summary>
    /// Set the audiosource threshold noise level before stopping recording
    /// <summary>
    [Tooltip("Sound noise level threshold before stopping recording")]
    public double audioLevelLowerThreshold = 0.02;
    /// <summary>
    /// How long to wait the sound level has to be below the lower threshold before stopping recording
    /// <summary>
    [Tooltip("How long to wait the sound level has to be below the lower threshold before stopping recording ( seconds )")]
    public double audioPauseWindow = 1;
    /// <summary>
    /// How long before the the clip is sent with the audio
    /// <summary>
    [Tooltip("Seconds before the clip that are sent with the audio ( seconds )")]
    public double audioStartWindow = 0.2;
    /// <summary>
    /// Set the audiosource sampling time during which the recording is checked for noise level
    /// <summary>
    [Tooltip("Sound noise level sampling window ( seconds )")]
    public double audioSamplingWindow = 0.1;

    /// <summary>
    /// Set the button to start and stop recording
    /// <summary>
    [Tooltip("Set the button to start and stop recording")]
    public Button startButton;
    /// <summary>
    /// Set the button to calibrate the noise level for automatic recording
    /// <summary>
    public Button calibrationButton;
    /// <summary>
    /// Transcription text
    /// <summary>
    public TMP_Text transcription;
    /// <summary>
    /// Response text
    /// <summary>
    public TMP_Text response;
    /// <summary>
    /// Noise level text
    /// <summary>
    public TMP_Text noiseLevel;
    /// <summary>
    /// Set the host input field
    /// <summary>
    public TMP_InputField hostInput;
    /// <summary>
    /// Set the port input field
    /// <summary>
    public TMP_InputField portInput;


    /// <summary>
    /// Set the image in the slots
    /// <summary>
    public Image[] image;
    /// <summary>
    /// Set the text in the slots
    /// <summary>
    public TMP_Text[] text;
    #endregion
    /// <summary>
    /// Event to be called when the request is started
    /// </summary>
    public UnityEvent requestStarted = new UnityEvent();
    /// <summary>
    /// Event to be called when the request is done. May not match with the audio playback time
    /// </summary>
    public UnityEvent requestDone = new UnityEvent();
    /// <summary>
    /// The url to post the audio file to
    /// </summary>
    private string url;
    /// <summary>
    /// The audio clip to record the microphone to
    /// </summary>
    private AudioClip clip;
    /// <summary>
    /// Is the microphone currently actually recording audio to be sent to the server
    /// </summary>
    private bool isRecording = false;
    /// <summary>
    /// Is the microphone activated by this script
    /// </summary>
    private bool isMicrophoneActivated = false;
    /// <summary>
    /// The maximum time to record audio for. Once this time is reached, the recording will loop back to the start, overwriting the oldest audio.
    /// </summary>
    private int maxRecordingTime = 300;
    /// <summary>
    /// Variable to keep track of the time
    /// </summary>
    private float timer = 0;
    /// <summary>
    /// The start position of the recording. It may be changed according to the position specified by the audio noise level detection.
    /// </summary>
    private int startPosition = 0;

    void Start()
    {
        this.url = (this.ssl ? "https://" : "http://") + this.host + ((this.port != "") ? ":" + this.port : "");
        // send a request to the server to check if it is running and the connection is successful
        UnityWebRequest request = UnityWebRequest.Get(this.url);
        request.SendWebRequest();
        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(request.error);
        }
        else
        {
            Debug.Log("Connection Successful!");
        }
        this.url = this.url + "/" + this.path + "?bot=" + this.bot + "&sender=" + this.sender_id;
        // start the recording for the audio noise level detection
        // StartRecording();
        if (this.startButton != null)
            this.startButton.onClick.AddListener(StartStopRecording);
        if (this.calibrationButton != null)
            this.calibrationButton.onClick.AddListener(autoCalibration);
        if (this.autoStart)
            this.StartRecording();
        if (this.hostInput != null)
            this.hostInput.text = this.host;
            this.hostInput.onEndEdit.AddListener(delegate { this.changeHost(this.hostInput.text); });
        if (this.portInput != null)
            this.portInput.text = this.port;
            this.portInput.onEndEdit.AddListener(delegate { this.changePort(this.portInput.text); });
    }
    void StartStopRecording()
    {
        if (this.isMicrophoneActivated)
        {
            this.StopRecording();
            if (this.startButton != null)
                this.startButton.GetComponentInChildren<TMP_Text>().text = "Start Recording";
            else
                Debug.Log("Button not linked");
        }
        else
        {
            this.StartRecording();
            if (this.startButton != null)
                this.startButton.GetComponentInChildren<TMP_Text>().text = "Stop Recording";
            else
                Debug.Log("Button not linked");

        }
    }

    void Update()
    {

        if (this.outputSource == null)
        {
            Debug.Log("No output source");
        }
        else
        {
            // if the audio is playing, do nothing
            if (this.outputSource.isPlaying)
            {
                return;
            }
            else
            {
                if (this.isMicrophoneActivated)
                {
                    // check the audio noise level over the sampling window is above the upper threshold
                    int position = Microphone.GetPosition(Microphone.devices[0]);
                    float audioLevel = Audio.getAudioLevel(this.clip, position, this.audioSamplingWindow);
                    // Debug.Log(audioLevel);
                    this.noiseLevel.text = audioLevel.ToString();
                    // start the recording if the audio level is above the upper threshold
                    if (!this.isRecording && (audioLevel > this.audioLevelUpperThreshold))
                    {
                        this.startPosition = position - (int)(this.audioStartWindow * this.inputSampleRate);
                        this.startPosition = this.startPosition < 0 ? 0 : this.startPosition;
                        this.isRecording = true;

                    }
                    // stop the recording if the audio level is below the lower threshold
                    if (this.isRecording && audioLevel < this.audioLevelLowerThreshold)
                    {
                        // timer to wait for the audio level to be below the lower threshold for the pause window
                        this.timer += Time.deltaTime;
                        if (this.timer > this.audioPauseWindow)
                        {
                            this.StopRecording();
                            this.isRecording = false;
                            this.SendAndPlay();
                            this.timer = 0;
                        }
                    }
                }
            }
        }


    }
    /// <summary>
    /// Starts and stops the calibration process
    /// </summary>
    public void autoCalibration()
    {
        if (this.isMicrophoneActivated)
        {
            this.StopRecording();
            float max; 
            float avg;
            (max, avg) = Audio.Calibration(this.clip);
            max = max * 0.8f;
            avg = avg * 0.8f;
            this.audioLevelUpperThreshold = max;
            this.audioLevelLowerThreshold = avg;
            if (this.calibrationButton != null)
                this.calibrationButton.GetComponentInChildren<TMP_Text>().text = "Re-Calibrate";
            else
                Debug.Log("Button not linked");
            if (this.autoStart)
                this.StartRecording();
        }
        else
        {
            this.StartRecording();
            if (this.calibrationButton != null)
                this.calibrationButton.GetComponentInChildren<TMP_Text>().text = "Stop Calibration";
            else
                Debug.Log("Button not linked");
        }
    }
    /// <summary>
    /// Start recording audio from the microphone
    /// </summary>
    public void StartRecording()
    {
        this.clip = Microphone.Start(Microphone.devices[0], true, this.maxRecordingTime, this.inputSampleRate);
        this.isMicrophoneActivated = true;
    }
    /// <summary>
    /// Stop recording audio from the microphone
    /// </summary>
    public void StopRecording()
    {
        int endPosition = Microphone.GetPosition(Microphone.devices[0]);
        Microphone.End(Microphone.devices[0]);
        this.clip = Audio.trimAudioClip(this.clip, this.startPosition, endPosition);
        this.isMicrophoneActivated = false;

    }
    /// <summary>
    /// Send the recorded audio to the server and play the response
    /// </summary>
    public void SendAndPlay()
    {
        this.requestStarted.Invoke();
        this.StartCoroutine(PostStreamAndPlay());
        if (this.processingSource != null)
            this.processingSource.Play();
    }

    /// <summary>
    /// Send the recorded audio to the server and play the response
    /// </summary>
    IEnumerator PostStreamAndPlay()
    {
        byte[] fileContent = Audio.ConvertWav(this.clip);
        UnityWebRequest request = new UnityWebRequest(this.url, "POST");
        UploadHandler uploader = new UploadHandlerRaw(fileContent);
        // the download handler is a custom one that automatically plays the audio in streaming mode
        StreamingPCMDownloadHandler downloader = new StreamingPCMDownloadHandler(this.outputSource, this.outputSampleRate, 1, pauseLength: 100);
        request.uploadHandler = uploader;
        request.downloadHandler = downloader;
        request.SetRequestHeader("Content-Type", "audio/wav");
        yield return request.SendWebRequest();
        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(request.error);
        }
        else
        {
            requestDone.Invoke();
        }
        // ServerConnectionSlots slots = GetComponent<ServerConnectionSlots>();
        StartCoroutine(this.GetSlots());
        // wait unitl the audio is done playing to avoid recording the response
        while (this.outputSource.isPlaying)
        {
            yield return null;
        }
        this.StartRecording();
        yield return null;
    }

    public IEnumerator GetSlots()
    {
        UnityWebRequest request = new UnityWebRequest(this.url, "GET");
        // the download handler is a custom one that automatically plays the audio in streaming mode
        DownloadHandlerBuffer downloader = new DownloadHandlerBuffer();
        request.downloadHandler = downloader;
        yield return request.SendWebRequest();
        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(request.error);
        }
        else
        {
            
            JsonData data = JsonMapper.ToObject(request.downloadHandler.text);
            
            for (int i = 0; i < data.Count; i++)
            {
                try{
                    for (int j = 0; j < data["titles"].Count; j++)
                    {
                        this.text[j].text = data["titles"][j].ToString();
                    }
                }
                catch (KeyNotFoundException e)
                {
                    Debug.Log(e);
                }
                try{
                    for (int j = 0; j < data["images"].Count; j++)
                    {
                        // decode bytes from base64
                        byte[] bytes = Convert.FromBase64String((data["images"][j].ToString()));
                        // save the bytes to a file
                        // string path = Application.dataPath + "/Temp/" + "image_" +j + ".jpg";
                        // File.WriteAllBytes(path, bytes);
                        Texture2D texture = new Texture2D(2, 2);
                        texture.LoadImage(bytes);
                        this.image[j].sprite = Sprite.Create(texture, new Rect(0, 0, texture.width, texture.height), new Vector2(0.5f, 0.5f));
                    }
                }
                catch (KeyNotFoundException e)
                {
                    Debug.Log(e);
                }
                try{
                    this.transcription.text = data["transcription"].ToString();
                }
                catch (KeyNotFoundException e)
                {
                    Debug.Log(e);
                } 
                try{
                    this.response.text = data["response"].ToString();
        
                }
                catch (KeyNotFoundException e)
                {
                    Debug.Log(e);
                }
            }
            Debug.Log("Slots Received!");
        }
        yield return null;
    }
    public void changeHost(string host)
    {
        this.host = host;
        Debug.Log("Host changed to " + host);
        this.url = (this.ssl ? "https://" : "http://") + this.host + ((this.port != "") ? ":" + this.port : "");
        this.url = this.url + "/" + this.path + "?sender=" + this.sender_id;
    }
    public void changePort(string port)
    {
        this.port = port;
        Debug.Log("Port changed to " + port);
        this.url = (this.ssl ? "https://" : "http://") + this.host + ((this.port != "") ? ":" + this.port : "");
        this.url = this.url + "/" + this.path + "?sender=" + this.sender_id;
    }
    public void changeActivationThreshold(string value)
    {
        this.audioLevelUpperThreshold = float.Parse(value);
        Debug.Log("Activation Threshold changed to " + value);
    }
    public void changeDeactivationThreshold(string value)
    {
        this.audioLevelLowerThreshold = float.Parse(value);
        Debug.Log("Deactivation Threshold changed to " + value);
    }
}

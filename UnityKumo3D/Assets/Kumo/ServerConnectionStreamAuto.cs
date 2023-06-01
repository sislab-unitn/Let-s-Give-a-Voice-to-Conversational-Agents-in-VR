using System.Text;
using System.Diagnostics;
// using System.Diagnostics;
using System.Threading.Tasks;
using System.Threading;
// using System.Diagnostics;
using System.Runtime.CompilerServices;
using System.Globalization;
// using System.Diagnostics;

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
    /// The path to post the audio file to
    /// </summary>
    [Tooltip("The path to post the audio file to")]
    public string tracker_path = "get_tracker";
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
    /// ignores the editor settings and loads the settings from the settings file
    /// </summary>
    public bool preloadSettings = true;
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
    /// Set the bot input field
    /// <summary>
    public TMP_InputField botInput;


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
    public TMP_Text urlText;
    public TMP_Text upperThresholdText;
    public TMP_Text lowerThresholdText;
    /// <summary>
    /// The url to post the audio file to
    /// </summary>
    private string url;
    /// <summary>
    /// The tracker url
    /// </summary>
    private string tracker_url;
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
    private bool isCalibrating = false;
    private bool keepStarting = true;
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
        // PlayerPrefs.DeleteAll();
        if (this.preloadSettings)
        {
            this.loadSettings();
        }
        const string glyphs= "abcdefghijklmnopqrstuvwxyz0123456789";
        string myString = "";
        for(int i=0; i<10; i++)
        {
            myString += glyphs[UnityEngine.Random.Range(0, glyphs.Length)];
        }
        this.sender_id = myString;
        // UnityEngine.Debug.Log("SSL: " + this.ssl);
        this.url = (this.ssl ? "https://" : "http://") + this.host + ((this.port != "") ? ":" + this.port : "");
        // UnityEngine.Debug.Log("URL: " + this.url);
        // send a request to the server to check if it is running and the connection is successful
        UnityWebRequest request = UnityWebRequest.Get(this.url);
        request.SendWebRequest();
        if (request.result != UnityWebRequest.Result.Success)
        {
            UnityEngine.Debug.Log(request.error);
        }
        else
        {
            UnityEngine.Debug.Log("Connection Successful!");
        }
        this.tracker_url = this.url + "/" + this.tracker_path + "?bot=" + this.bot + "&sender=" + this.sender_id;
        this.url = this.url + "/" + this.path + "?bot=" + this.bot + "&sender=" + this.sender_id;
        // UnityEngine.Debug.Log("URL: " + this.url);
        // start the recording for the audio noise level detection
        // StartRecording();
        if (this.startButton != null)
            this.startButton.onClick.AddListener(StartStopRecording);
        if (this.calibrationButton != null)
            this.calibrationButton.onClick.AddListener(autoCalibration);
        if (this.autoStart)
            this.StartStopRecording();
        if (this.hostInput != null)
            this.hostInput.text = this.host;
        this.hostInput.onEndEdit.AddListener(delegate { this.changeHost(this.hostInput.text); });
        if (this.portInput != null)
            this.portInput.text = this.port;
        this.portInput.onEndEdit.AddListener(delegate { this.changePort(this.portInput.text); });
        if (this.urlText != null)
            this.urlText.text = this.url;
        if (this.upperThresholdText != null)
            this.upperThresholdText.text = this.audioLevelUpperThreshold.ToString();
        if (this.lowerThresholdText != null)
            this.lowerThresholdText.text = this.audioLevelLowerThreshold.ToString();
        if (this.botInput != null)
        {
            this.botInput.text = this.bot;
            this.botInput.onEndEdit.AddListener(delegate { this.changeBot(this.botInput.text); });
        }
    }
    public void trueStart()
    {
        this.StartRecording();
        this.keepStarting = true;
    }
    public void trueStop()
    {
        this.keepStarting = false;
        UnityEngine.Debug.Log("Stop");
        this.StopRecording();
    }
    public void StartStopRecording()
    {
        UnityEngine.Debug.Log("StartStopRecording");
        if (this.isMicrophoneActivated)
        {
            this.trueStop();

            if (this.startButton != null)
                this.startButton.GetComponentInChildren<TMP_Text>().text = "Start Recording";
            else
                UnityEngine.Debug.Log("Button not linked");
            if (this.calibrationButton != null)
                this.calibrationButton.enabled = true;
            else
                UnityEngine.Debug.Log("Button not linked");

        }
        else if (this.outputSource.isPlaying){
            this.keepStarting = false;
            if (this.startButton != null)
                this.startButton.GetComponentInChildren<TMP_Text>().text = "Start Recording";
            else
                UnityEngine.Debug.Log("Button not linked");
        }
        else
        {
            this.trueStart();
            if (this.startButton != null)
                this.startButton.GetComponentInChildren<TMP_Text>().text = "Stop Recording";
            else
                UnityEngine.Debug.Log("Button not linked");
            if (this.calibrationButton != null)
                this.calibrationButton.enabled = false;
            else
                UnityEngine.Debug.Log("Button not linked");

        }
    }
    void loadSettings()
    {
        this.ssl = (PlayerPrefs.GetInt("ssl", 0) == 1);
        this.host = PlayerPrefs.GetString("host", "localhost");
        this.port = PlayerPrefs.GetString("port", "8000");
        if (String.Equals(this.name, "ServerConnectionStreamAuto Triage", StringComparison.OrdinalIgnoreCase))
        {
            this.bot = PlayerPrefs.GetString("bot", "triage_bot");
            
            this.bot = "triage_bot";
        }
        else if (String.Equals(this.name, "ServerConnectionStreamAuto Anamnesis", StringComparison.OrdinalIgnoreCase))
        {
            this.bot = PlayerPrefs.GetString("bot", "anamnesis_bot");
            
            this.bot = "anamnesis_bot";
        }
        else
        {
            this.bot = PlayerPrefs.GetString("bot", "bot");
        }
        UnityEngine.Debug.Log("Bot: " + this.bot);
        // this.sender_id = PlayerPrefs.GetString("sender_id", "user");
        this.path = PlayerPrefs.GetString("path", "audio_converse_stream");
        this.tracker_path = PlayerPrefs.GetString("tracker_path", "get_tracker");
        this. audioLevelUpperThreshold = PlayerPrefs.GetFloat("audioLevelUpperThreshold", 0.03f);
        this.audioLevelLowerThreshold = PlayerPrefs.GetFloat("audioLevelLowerThreshold", 0.02f);
    }
    void saveSettings()
    {
        PlayerPrefs.SetInt("ssl", (this.ssl ? 1 : 0));
        PlayerPrefs.SetString("host", this.host);
        PlayerPrefs.SetString("port", this.port);
        PlayerPrefs.SetString("bot", this.bot);
        // PlayerPrefs.SetString("sender_id", this.sender_id);
        PlayerPrefs.SetString("path", this.path);
        PlayerPrefs.SetFloat("audioLevelUpperThreshold", (float)this.audioLevelUpperThreshold);
        PlayerPrefs.SetFloat("audioLevelLowerThreshold", (float)this.audioLevelLowerThreshold);
        PlayerPrefs.Save();
    }
    void Update()
    {

        if (this.outputSource == null)
        {
            UnityEngine.Debug.Log("No output source");
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
                if (this.isMicrophoneActivated && !(this.isCalibrating))
                {
                    // check the audio noise level over the sampling window is above the upper threshold
                    int position = Microphone.GetPosition(Microphone.devices[0]);
                    float audioLevel = Audio.getAudioLevel(this.clip, position, this.audioSamplingWindow);
                    // UnityEngine.Debug.Log(audioLevel);
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
                else if (this.isCalibrating && this.isMicrophoneActivated)
                {
                    // check the audio noise level over the sampling window is above the upper threshold
                    int position = Microphone.GetPosition(Microphone.devices[0]);
                    float audioLevel = Audio.getAudioLevel(this.clip, position, this.audioSamplingWindow);
                    // UnityEngine.Debug.Log(audioLevel);
                    this.noiseLevel.text = audioLevel.ToString();
                    this.audioLevelUpperThreshold = (audioLevel * 0.8f > this.audioLevelUpperThreshold) ? audioLevel * 0.8f : this.audioLevelUpperThreshold;
                    if (this.upperThresholdText != null)
                        this.upperThresholdText.text = this.audioLevelUpperThreshold.ToString();
                    else
                        UnityEngine.Debug.Log("Upper threshold text not linked");
                    // this.audioLevelUpperThreshold = this.audioLevelUpperThreshold * 0.8f;
                    this.audioLevelLowerThreshold = 1.2f * audioLevel;
                    if (this.lowerThresholdText != null)
                        this.lowerThresholdText.text = this.audioLevelLowerThreshold.ToString();
                    else
                        UnityEngine.Debug.Log("Lower threshold text not linked");
                    // this.audioLevelLowerThreshold = this.audioLevelLowerThreshold * 1.2f;
                }
            }
        }
        // this.hostInput.isFocused


    }
    /// <summary>
    /// Starts and stops the calibration process
    /// </summary>
    public void autoCalibration()
    {
        if (this.isCalibrating)
        {
            this.StopRecording();
            
            if (this.calibrationButton != null)
                this.calibrationButton.GetComponentInChildren<TMP_Text>().text = "Re-Calibrate";
            else
                UnityEngine.Debug.Log("Button not linked");
            if (this.startButton != null)
                this.startButton.enabled = true;
            else
                UnityEngine.Debug.Log("Button not linked");
            if (this.autoStart)
                this.StartRecording();
                
            this.isCalibrating = false;
        }
        else
        {
            this.audioLevelLowerThreshold = 1.0f;
            this.audioLevelUpperThreshold = 0.0f;
            this.StartRecording();
            this.isCalibrating = true;

            if (this.calibrationButton != null)
                this.calibrationButton.GetComponentInChildren<TMP_Text>().text = "Stop Calibration";
            else
                UnityEngine.Debug.Log("Button not linked");
            if (this.startButton != null)
                this.startButton.enabled = false;
            else
                UnityEngine.Debug.Log("Button not linked");
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
        if (endPosition > this.startPosition){
            this.clip = Audio.trimAudioClip(this.clip, this.startPosition, endPosition);
        }
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

        UnityEngine.Debug.Log("Sending request");
        UnityEngine.Debug.Log(url);
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
            UnityEngine.Debug.Log(request.error);
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
        if (this.keepStarting)
            this.StartRecording();
        yield return null;
    }

    public IEnumerator GetSlots()
    {
        UnityWebRequest request = new UnityWebRequest(this.tracker_url, "GET");
        // the download handler is a custom one that automatically plays the audio in streaming mode
        DownloadHandlerBuffer downloader = new DownloadHandlerBuffer();
        request.downloadHandler = downloader;
        yield return request.SendWebRequest();
        if (request.result != UnityWebRequest.Result.Success)
        {
            UnityEngine.Debug.Log(request.error);
        }
        else
        {

            JsonData data = JsonMapper.ToObject(request.downloadHandler.text);

            for (int i = 0; i < data.Count; i++)
            {
                try
                {
                    for (int j = 0; j < data["titles"].Count; j++)
                    {
                        this.text[j].text = data["titles"][j].ToString();
                    }
                }
                catch (KeyNotFoundException e)
                {
                    UnityEngine.Debug.Log(e);
                }
                try
                {
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
                    UnityEngine.Debug.Log(e);
                }
                try
                {
                    this.transcription.text = data["transcription"].ToString();
                }
                catch (KeyNotFoundException e)
                {
                    UnityEngine.Debug.Log(e);
                }
                try
                {
                    this.response.text = data["response"].ToString();

                }
                catch (KeyNotFoundException e)
                {
                    UnityEngine.Debug.Log(e);
                }
            }
            UnityEngine.Debug.Log("Slots Received!");
        }
        yield return null;
    }
    public void changeHost(string host)
    {
        this.host = host;
        UnityEngine.Debug.Log("Host changed to " + host);
        this.url = (this.ssl ? "https://" : "http://") + this.host + ((this.port != "") ? ":" + this.port : "");
        this.url = this.url + "/" + this.path + "?bot=" + this.bot + "&sender=" + this.sender_id;
        this.urlText.text = this.url;
        this.saveSettings();
    }
    public void changePort(string port)
    {
        this.port = port;
        UnityEngine.Debug.Log("Port changed to " + port);
        this.url = (this.ssl ? "https://" : "http://") + this.host + ((this.port != "") ? ":" + this.port : "");
        this.url = this.url + "/" + this.path + "?bot=" + this.bot + "&sender=" + this.sender_id;
        this.urlText.text = this.url;
        this.saveSettings();
    }
    public void changeActivationThreshold(string value)
    {
        this.audioLevelUpperThreshold = float.Parse(value);
        UnityEngine.Debug.Log("Activation Threshold changed to " + value);
        this.saveSettings();
    }
    public void changeDeactivationThreshold(string value)
    {
        this.audioLevelLowerThreshold = float.Parse(value);
        UnityEngine.Debug.Log("Deactivation Threshold changed to " + value);
        this.saveSettings();
    }
    public void changeBot(string bot)
    {
        this.bot = bot;
        UnityEngine.Debug.Log("Bot changed to " + bot);
        this.url = (this.ssl ? "https://" : "http://") + this.host + ((this.port != "") ? ":" + this.port : "");
        this.url = this.url + "/" + this.path + "?bot=" + this.bot + "&sender=" + this.sender_id;
        this.urlText.text = this.url;
        this.saveSettings();
    }
}
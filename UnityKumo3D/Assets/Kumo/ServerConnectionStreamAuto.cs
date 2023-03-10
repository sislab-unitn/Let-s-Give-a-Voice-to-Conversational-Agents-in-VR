using System.Collections;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.Networking;
using TMPro;
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
    public string host;
    /// <summary>
    /// The port to post the audio file to
    /// </summary>
    [Tooltip("The port to post the audio file to")]
    public string port;
    /// <summary>
    /// The path to post the audio file to
    /// </summary>
    [Tooltip("The path to post the audio file to")]
    public string path;
    /// <summary>
    /// The sender id for rasa to use
    /// </summary>
    [Tooltip("The sender id for rasa to use")]
    public string sender_id;
    /// <summary>
    /// Use SSL or not
    /// </summary>
    [Tooltip("Use SSL or not")]
    public bool ssl;
    /// <summary>
    /// input audio sample rate
    /// <summary>
    [Tooltip("input audio sample rate")]
    public int inputSampleRate;
    /// <summary>
    /// output audio sample rate
    /// <summary>
    [Tooltip("output audio sample rate")]
    public int outputSampleRate;

    /// <summary>
    /// Set the outputsource
    /// <summary>
    [Tooltip("audiosource from where to play the response")]
    public AudioSource outputSource;

    /// <summary>
    /// Set the playback of processing sound
    /// <summary>
    [Tooltip("Set the playback of processing sound")]
    public AudioSource processingSource;

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

    public TMP_Text transcription;
    public TMP_Text response;
    public TMP_Text noiseLevel;
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
        this.url = this.url + "/" + this.path + "?sender=" + this.sender_id;
        // start the recording for the audio noise level detection
        StartRecording();
    }

    void Update()
    {
        // if the audio is playing, do nothing
        if (outputSource.isPlaying)
        {
            return;
        }
        else
        {
            // check the audio noise level over the sampling window is above the upper threshold
            int position = Microphone.GetPosition(Microphone.devices[0]);
            float audioLevel = Audio.getAudioLevel(this.clip, position, this.audioSamplingWindow);
            Debug.Log(audioLevel);
            noiseLevel.text = audioLevel.ToString();
            // start the recording if the audio level is above the upper threshold
            if (!this.isRecording && (audioLevel > this.audioLevelUpperThreshold))
            {
                this.startPosition = position - (int)(this.audioStartWindow * this.inputSampleRate);
                startPosition = startPosition < 0 ? 0 : startPosition;
                this.isRecording = true;

            }
            // stop the recording if the audio level is below the lower threshold
            if (this.isRecording && audioLevel < this.audioLevelLowerThreshold)
            {
                // timer to wait for the audio level to be below the lower threshold for the pause window
                timer += Time.deltaTime;
                if (timer > this.audioPauseWindow)
                {
                    StopRecording();
                    this.isRecording = false;
                    SendAndPlay();
                    timer = 0;
                }
            }
        }


    }
    /// <summary>
    /// Start recording audio from the microphone
    /// </summary>
    public void StartRecording()
    {
        this.clip = Microphone.Start(Microphone.devices[0], true, this.maxRecordingTime, this.inputSampleRate);
    }
    /// <summary>
    /// Stop recording audio from the microphone
    /// </summary>
    public void StopRecording()
    {
        int endPosition = Microphone.GetPosition(Microphone.devices[0]);
        Microphone.End(Microphone.devices[0]);
        this.clip = Audio.trimAudioClip(this.clip, this.startPosition, endPosition);

    }
    /// <summary>
    /// Send the recorded audio to the server and play the response
    /// </summary>
    public void SendAndPlay()
    {
        requestStarted.Invoke();
        StartCoroutine(PostStreamAndPlay());
        processingSource.Play();
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
        StreamingPCMDownloadHandler downloader = new StreamingPCMDownloadHandler(this.outputSource, this.outputSampleRate, 1, pauseLength : 100);
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
        ServerConnectionSlots slots = GetComponent<ServerConnectionSlots>();
        StartCoroutine(slots.GetSlots());
        // wait unitl the audio is done playing to avoid recording the response
        while (this.outputSource.isPlaying)
        {
            yield return null;
        }
        StartRecording();
        yield return null;
    }

}

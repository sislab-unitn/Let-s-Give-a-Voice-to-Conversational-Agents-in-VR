using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.Networking;
using UnityEngine.UI;
using System.IO;
using System;
using System.Globalization;
using System.Text;
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
    #endregion
    public UnityEvent requestStarted = new UnityEvent();
    public UnityEvent requestDone = new UnityEvent();
    private string url;
    // recorded clip
    private AudioClip clip;
    private bool isRecording = false;
    private int maxRecordingTime = 300;
    private float timer = 0;
    private int startPosition = 0;
    void Start()
    {
        this.url = (this.ssl ? "https://" : "http://") + this.host + ((this.port != "") ? ":" + this.port : "");
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
        StartRecording();
    }

    // Update is called once per frame
    void Update()
    {
        if (outputSource.isPlaying)
        {
            return;
        }else
        {
            int position = Microphone.GetPosition(Microphone.devices[0]);
            float audioLevel = Audio.getAudioLevel(this.clip, position, this.audioSamplingWindow);
            if( !this.isRecording ){
                if (audioLevel > this.audioLevelUpperThreshold) 
                { 
                    // StartRecording();
                    this.startPosition = position - (int)(this.audioStartWindow * this.inputSampleRate) ;
                    startPosition = startPosition < 0 ? 0 : startPosition;
                    this.isRecording = true;
                }
            }
            if (this.isRecording && audioLevel < this.audioLevelLowerThreshold)
            {
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
    public void StartRecording()
    {
        this.clip = Microphone.Start(Microphone.devices[0], true, this.maxRecordingTime, this.inputSampleRate);
        // this.isRecording = true;
    }
    public void StopRecording()
    {
        int  endPosition = Microphone.GetPosition(Microphone.devices[0]);
        Microphone.End(Microphone.devices[0]);
       
        this.clip = Audio.trimAudioClip(this.clip, this.startPosition, endPosition);
        // this.outputSource.PlayOneShot(this.clip);

    }
    public void SendAndPlay()
    {
        requestStarted.Invoke();
        StartCoroutine(PostStreamAndPlay());
        // play audioclip
        processingSource.Play();
    }


    IEnumerator PostStreamAndPlay()
    {
        byte[] fileContent = Audio.ConvertWav(this.clip);
        UnityWebRequest request = new UnityWebRequest(this.url, "POST");
        UploadHandler uploader = new UploadHandlerRaw(fileContent);
        // the download handler is a custom one that automatically plays the audio in streaming mode
        StreamingPCMDownloadHandler downloader = new StreamingPCMDownloadHandler(this.outputSource, this.outputSampleRate, 1);
        request.uploadHandler = uploader;
        request.downloadHandler = downloader;
        request.SetRequestHeader("Content-Type", "audio/wav");
        request.chunkedTransfer = true;
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
    // This comes from SoundWav module


}

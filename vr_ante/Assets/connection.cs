using System.Collections;
using System.Collections.Generic;
using UnityEngine;

using UnityEngine.Events;
using UnityEngine.Networking;
using UnityEngine.UI;

using System;
using System.IO;
using System.Threading;
using System.Diagnostics;


public class connection : MonoBehaviour
{
    public AgentTalk agentTalk;

    private bool keepStarting = true;
    private bool isMicrophoneActivated = false;
    private bool isCalibrating = false;
    private bool isRecording = false;
    private int maxRecordingTime = 100;

    public AudioSource outputSource;

    private AudioClip clip;
    private AudioClip trimmed_clip;

    public double audioSamplingWindow = 0.1;

    public double audioLevelUpperThreshold = 0.03;
    public double audioLevelLowerThreshold = 0.01;

    private int startPosition = 0;
    private int endPosition = 0;

    public double audioStartWindow = 0.2;

    public int inputSampleRate = 48000;
    public int outputSampleRate = 24000;

    // private float timer = 0;
    public Stopwatch timer = new Stopwatch();

    public double audioPauseWindow = 3;

    public double request_interval = 2;
    public Stopwatch request_interval_timer = new Stopwatch();

    public string host = "localhost";
    public string port = "8000";
    public string path = "pipeline";

    private bool request_sent = false;
    private bool request_done = false;

    public UnityEvent presentationDone = new UnityEvent();

    private bool greet_done = false;

    private int maxTurns = 3;
    private int curTurns = 0;

    private string[] files = {"avatar_responses/first", "avatar_responses/second"};

    void Start()
    {
        StartCoroutine(WaitCoroutine());
    }

    IEnumerator WaitCoroutine()
    {
        //Print the time of when the function is first called.
        //yield on a new YieldInstruction that waits for 5 seconds.
        yield return new WaitForSecondsRealtime(2);

        presentationDone.AddListener(StartRecording);

        GameObject newGameObject = new GameObject("AgentTalk");
        agentTalk = newGameObject.AddComponent<AgentTalk>();
        agentTalk.PlayIntro(this.outputSource, this.presentationDone);

        // UnityEngine.Debug.Log("Start");
        // this.StartRecording();
        this.keepStarting = true;

        yield return null;

    }

    public void StartRecording()
    {
        UnityEngine.Debug.Log(Microphone.devices[0].ToString());
        this.clip = Microphone.Start(Microphone.devices[0], true, this.maxRecordingTime, this.inputSampleRate);
        this.isMicrophoneActivated = true;
    }

    public void StopRecording()
    {
        Microphone.End(Microphone.devices[0]);
        this.isMicrophoneActivated = false;
    }

    public void Trim()
    {
        // int endPosition = Microphone.GetPosition(Microphone.devices[0]);

        UnityEngine.Debug.Log(this.endPosition);
        UnityEngine.Debug.Log(this.startPosition);
        if (this.endPosition > this.startPosition)
        {
            UnityEngine.Debug.Log("trim clip");
            this.trimmed_clip = Audio.trimAudioClip(this.clip, this.startPosition, this.endPosition);
        }
        else
        {
            UnityEngine.Debug.Log("copy clip");
            this.trimmed_clip = Audio.duplicateAudioClip(this.clip);
        }
    }

    public void startTimer(Stopwatch t)
    {
        // this.request_interval_timer.Reset();
        // this.request_interval_timer.Start();
        t.Reset();
        t.Start();
    }

    public void stopTimer(Stopwatch t)
    {
        t.Stop();
        // this.request_interval_timer.Stop();
    }

    void Update()
    {
        if (this.outputSource == null)
        {
            UnityEngine.Debug.Log("No output source");
        }
        else
        {
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

                    // start the recording if the audio level is above the upper threshold
                    if (!this.isRecording && (audioLevel > this.audioLevelUpperThreshold))
                    {
                        UnityEngine.Debug.Log("audio level is higher");
                        this.startPosition = Microphone.GetPosition(Microphone.devices[0]);
                        // this.startPosition = position - (int)(this.audioStartWindow * this.inputSampleRate);
                        this.isRecording = true;
                        this.startTimer(request_interval_timer);
                    }

                    if (this.isRecording && audioLevel > this.audioLevelUpperThreshold)
                    {
                        // this.timer = 0;
                        timer.Reset();
                        this.stopTimer(timer);
                    }
            
                    if (this.isRecording && this.greet_done) 
                    {
                        float elapsed_time = request_interval_timer.ElapsedMilliseconds / 1000f;
                        if (elapsed_time > request_interval) 
                        {
                            UnityEngine.Debug.Log(elapsed_time);
                            UnityEngine.Debug.Log("elapsed bigger");
                            this.endPosition = Microphone.GetPosition(Microphone.devices[0]);
                            this.SendClip();
                            this.startTimer(request_interval_timer);
                        }
                    }
                    // stop the recording if the audio level is below the lower threshold
                    if (this.isRecording && audioLevel < this.audioLevelLowerThreshold)
                    {
                        float elapsed_time;
                        if (timer.Elapsed.TotalSeconds == 0)
                        {
                            timer.Start();
                            // this.startTimer(timer);
                            elapsed_time = 0;
                        }
                        else {
                            elapsed_time = timer.ElapsedMilliseconds / 1000f;
                        }
                        UnityEngine.Debug.Log(elapsed_time);
                        // UnityEngine.Debug.Log("audio level is lower");
                        // UnityEngine.Debug.Log(Time.deltaTime);
                        // this.timer += Time.deltaTime;
                        
                        if (elapsed_time > audioPauseWindow)
                        {
                            UnityEngine.Debug.Log("pause bigger");
                            UnityEngine.Debug.Log(elapsed_time);
                            this.endPosition = Microphone.GetPosition(Microphone.devices[0]);
                            this.StopRecording();
                            this.isRecording = false;
                            if (!greet_done) 
                            {
                                UnityEngine.Debug.Log("start greeting");
                                this.Trim();
                                // SavWav.Save("file.wav", this.trimmed_clip);
                                this.agentTalk.Greet(this.outputSource, this.trimmed_clip, this.presentationDone);
                                this.greet_done = true;
                            }
                            else
                            {
                                UnityEngine.Debug.Log(this.curTurns);
                                UnityEngine.Debug.Log(this.maxTurns);
                                if (this.curTurns == this.maxTurns - 1)
                                {
                                    this.keepStarting = false;
                                    this.agentTalk.PlayBye(this.outputSource);
                                }
                                else
                                {
                                    StartCoroutine(Play());
                                    this.stopTimer(request_interval_timer);
                                    this.curTurns += 1;
                                }
                            }
                            timer.Reset();
                            this.stopTimer(timer);
                        }
                    }
                }
            }
        }
    }

    IEnumerator Play()
    {
        // AudioClip resp = Resources.Load<AudioClip>(this.files[this.curTurns]);
        if (request_sent)
        {
            while (!request_done)
            {
                yield return null;
            }
            AudioClip resp = outputSource.clip;
            outputSource.PlayOneShot(resp);
        }
        else 
        {
            SendClip();
            while (!request_done)
            {
                yield return null;
            }
            AudioClip resp = outputSource.clip;
            outputSource.PlayOneShot(resp);
        }
        request_sent = false;
        request_done = false;
        while (this.outputSource.isPlaying)
        {
            yield return null;
        }
        if (this.keepStarting)
        {
            this.StartRecording();
        }
        yield return null;
    }

    public void SendClip()
    {
        this.Trim();
        // SavWav.Save("file.wav", this.trimmed_clip);
        StartCoroutine(PostStream());
        request_sent = true;
    }

    IEnumerator PostStream()
    {
        byte[] fileContent = Audio.ConvertWav(this.trimmed_clip);

        UnityEngine.Debug.Log("Byte content");
        UnityEngine.Debug.Log(fileContent.Length);

        string url = "http://" + this.host + ":" + this.port + "/" + this.path;


        UnityEngine.Debug.Log(url);
        UnityEngine.Debug.Log("Sending request");
        // UnityEngine.Debug.Log(url);
        UnityWebRequest request = new UnityWebRequest(url, "POST");
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
            if (this.isRecording)
            {
                SendClip();
            }
            request_done = true;
        }
       
        yield return null;
    }

}


using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;
using System.IO;
using System;
using System.Globalization;
using System.Text;
public class LoggingDownloadHandler : DownloadHandlerScript {

    // Standard scripted download handler - allocates memory on each ReceiveData callback
    public AudioClip clip;
    public int sampleRate;
    public int channels;
    private List<float> f_decoding;
    private AudioSource source;
    private DateTime timer;
    public LoggingDownloadHandler(): base() {

    }

    // Pre-allocated scripted download handler
    // reuses the supplied byte array to deliver data.
    // Eliminates memory allocation.

    public LoggingDownloadHandler(byte[] buffer): base(buffer) {
    }

     public LoggingDownloadHandler(AudioSource source): base() {
        this.sampleRate = 16000;
        this.channels = 1;
        this.f_decoding = new List<float>();
        this.source = source;
    }
    // Required by DownloadHandler base class. Called when you address the 'bytes' property.

    protected override byte[] GetData() { return null; }

    // Called once per frame when data has been received from the network.

    protected override bool ReceiveData(byte[] data, int dataLength) {
        if(data == null || data.Length < 1) {
            Debug.Log("LoggingDownloadHandler :: ReceiveData - received a null/empty buffer");
            return false;
        }
        for(int i = 0; i < dataLength; i += 2)
        {
            int sample = BitConverter.ToInt16(data, i);
            this.f_decoding.Add(sample / 32768.0f);
        }
        if (this.source.isPlaying)
        {
            Debug.Log("LoggingDownloadHandler :: ReceiveData - received " + dataLength + " bytes, but source is playing");
        }else{
            this.clip = AudioClip.Create("Response", this.f_decoding.Count, this.channels, this.sampleRate, false,false);
            this.clip.SetData(this.f_decoding.ToArray(), 0);
            this.f_decoding.Clear();
            this.source.PlayOneShot(this.clip);
            this.timer = DateTime.Now;
        }
       
        Debug.Log(string.Format("LoggingDownloadHandler :: ReceiveData - received {0} bytes", dataLength));
        return true;
    }

    // Called when all data has been received from the server and delivered via ReceiveData.

    protected override void CompleteContent() {
        DateTime time2 = DateTime.Now;
        TimeSpan timeSpan = time2.Subtract(this.timer);
        Debug.Log(timeSpan.TotalMilliseconds);
        Debug.Log(this.source.clip.length);
        while(timeSpan.TotalSeconds < this.source.clip.length)
        {
            Debug.Log("LoggingDownloadHandler :: CompleteContent - waiting for audio to finish");
            time2 = DateTime.Now;
            timeSpan = time2.Subtract(this.timer);
            
        }
        Debug.Log("LoggingDownloadHandler :: CompleteContent - DOWNLOAD COMPLETE!");
        this.clip = AudioClip.Create("Response", this.f_decoding.Count, this.channels, this.sampleRate, false,false);
        this.clip.SetData(this.f_decoding.ToArray(), 0);
        this.f_decoding.Clear();
        this.source.PlayOneShot(this.clip);
        // AudioClip clip = AudioClip.Create("Response", f_decoding.Count, channels, sampleRate, false,false);
        // clip.SetData(f_decoding.ToArray(), 0);
        // f_decoding.Clear();
        // source.PlayOneShot(clip);
        
    }

    // Called when a Content-Length header is received from the server.

    protected override void ReceiveContentLengthHeader(ulong contentLength) {
        Debug.Log(string.Format("LoggingDownloadHandler :: ReceiveContentLength - length {0}", contentLength));
    }

}
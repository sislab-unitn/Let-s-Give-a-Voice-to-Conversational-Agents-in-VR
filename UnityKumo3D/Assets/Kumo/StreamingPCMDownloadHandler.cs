using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.Networking;
using System;
using System.Threading.Tasks;
public class StreamingPCMDownloadHandler : DownloadHandlerScript
{

    // Standard scripted download handler - allocates memory on each ReceiveData callback
    public AudioClip clip;
    public int sampleRate;
    public int channels;
    private List<float> f_decoding;
    private AudioSource source;
    private DateTime timer;
    private byte oddByte;
    private bool oddByteSet = false;
    private UnityEvent audioChanged;
    private int pauseLength = 100;
    // private double downloadRate = 0;
    // private double timeAsDouble = 0;
    public StreamingPCMDownloadHandler() : base()
    {

    }

    // Pre-allocated scripted download handler
    // reuses the supplied byte array to deliver data.
    // Eliminates memory allocation.

    public StreamingPCMDownloadHandler(byte[] buffer) : base(buffer)
    {
    }

    public StreamingPCMDownloadHandler(AudioSource source, int sampleRate = 16000, int channels = 1, UnityEvent audioChanged = null, int pauseLength = 100) : base()
    {
        this.sampleRate = sampleRate;
        this.channels = channels;
        this.f_decoding = new List<float>();
        this.source = source;
        this.audioChanged = audioChanged;
        this.pauseLength = pauseLength;
    }

    // Required by DownloadHandler base class. Called when you address the 'bytes' property.

    protected override byte[] GetData() { return null; }

    // function to detect if a pause is detected in the audio, and stop the playing if the data is not received
    // the pause is coded by a number of 0 in the audio stream
    private int PauseDetector(byte[] data,int skip, int length)
    {
        bool pause = false;
        int count = 0;
        int position = -1;
        for (int i = skip; i < length; i += 2)
        {
            int sample = BitConverter.ToInt16(data, i);
            if (sample == 0)
            {
                count++;
            }
            else
            {
                count = 0;
                position = i;
            }
        }

        if (count == this.pauseLength)
        {
            pause = true;
        }
        return (pause ? position : -1);
    }

    // function to fix the very edge case when the data is not a multiple of 2
    private  (int,int) OddByteFix(byte[] data, int length)
    {
        int skip = this.oddByteSet ? 1 : 0;
        // if we have an odd byte from the last call, we need to prepend it to the data
        if (this.oddByteSet)
        {
            byte[] first = new byte[2];
            first[0] = this.oddByte;
            first[1] = data[0];
            int sample = BitConverter.ToInt16(first, 0);
            this.f_decoding.Add(sample / 32768.0f);
            this.oddByteSet = false;
            skip = 1;
        }
        // if the data is not a multiple of 2, we need to save the last byte for the next call
        if ( (length-skip) % 2 == 1)
        {
            this.oddByte = data[length - 1];
            this.oddByteSet = true;
            length -= 1;
        }

        return  (skip,length);
    }
    // Called once per frame when data has been received from the network.
    // here i decode the audio and play it using the audio player
    protected override bool ReceiveData(byte[] data, int dataLength)
    {
        Debug.Log("StreamingPCMDownloadHandler :: ReceiveData - received " + dataLength + " bytes");
        if (data == null || data.Length < 1)
        {
            Debug.Log("StreamingPCMDownloadHandler :: ReceiveData - received a null/empty buffer");
            return false;
        }
        // if the data is not a multiple of 2, we have a problem
        int skip = 0;
        // Debug.Log("StreamingPCMDownloadHandler :: ReceiveData - dataLength: " + dataLength);
        // Debug.Log("StreamingPCMDownloadHandler :: ReceiveData - oddByteSet: " + this.oddByteSet);
        // Debug.Log("StreamingPCMDownloadHandler :: ReceiveData - skip: " + skip);
        (skip,dataLength) = this.OddByteFix(data, dataLength);
        // Debug.Log("StreamingPCMDownloadHandler :: ReceiveData - dataLength: " + dataLength);
        // Debug.Log("StreamingPCMDownloadHandler :: ReceiveData - oddByteSet: " + this.oddByteSet);
        // Debug.Log("StreamingPCMDownloadHandler :: ReceiveData - skip: " + skip);
        int pause = this.PauseDetector(data,skip, dataLength);
        if (pause == -1)
        {
            for (int i = skip; i < dataLength; i += 2)
            {
                int sample = BitConverter.ToInt16(data, i);
                this.f_decoding.Add(sample / 32768.0f);
            }
        }
        else
        {
            Debug.Log("StreamingPCMDownloadHandler :: ReceiveData - pause detected - dataLength: " + pause);
            for (int i = skip; i < pause; i += 2)
            {
                int sample = BitConverter.ToInt16(data, i);
                this.f_decoding.Add(sample / 32768.0f);
            }
            if (!this.source.isPlaying)
            {
                this.clip = AudioClip.Create("Response", this.f_decoding.Count, this.channels, this.sampleRate, stream: false);
                this.clip.SetData(this.f_decoding.ToArray(), 0);
                this.f_decoding.Clear();
                this.source.clip = this.clip;
                if (this.audioChanged != null)
                {
                    this.audioChanged.Invoke();
                }
                this.source.PlayOneShot(this.clip);
                this.timer = DateTime.Now;
            }
            for (int i = pause; i < dataLength; i += 2)
            {
                int sample = BitConverter.ToInt16(data, i);
                this.f_decoding.Add(sample / 32768.0f);
            }

        }

        // double delta = Time.timeAsDouble - this.timeAsDouble;
        // this.downloadRate = this.downloadRate * 0.5 + 0.5* (double)dataLength / delta;
        // this.timeAsDouble = Time.timeAsDouble;
        // Debug.Log("StreamingPCMDownloadHandler :: ReceiveData - download rate: " + this.downloadRate);
        // // check if i have enough data to play without stutteroing
        // Debug.Log("StreamingPCMDownloadHandler :: ReceiveData - delta: " + (double) ((double)this.f_decoding.Count/(double)this.sampleRate));
        // Debug.Log("StreamingPCMDownloadHandler :: ReceiveData - delta: " + delta);


        return true;
    }

    // Called when all data has been received from the server and delivered via ReceiveData.
    // I call the audio player to empty the buffer here and play the audio
    protected override void CompleteContent()
    {
        if (this.f_decoding.Count < 1)
        {
            Debug.Log("StreamingPCMDownloadHandler :: CompleteContent - no data to play");
        }
        else
        {
            // i need to play the audio delayed by the amount of time it takes finish playing the current audio
            if(this.clip != null && this.source.isPlaying)
            {
                DateTime time2 = DateTime.Now;
                TimeSpan timeSpan = time2.Subtract(this.timer);
                // missing time to wait before playing the audio)
                float missing = this.clip.length - timeSpan.Seconds;

                Debug.Log("StreamingPCMDownloadHandler :: CompleteContent - DOWNLOAD COMPLETE!");
                this.clip = AudioClip.Create("Response", this.f_decoding.Count, this.channels, this.sampleRate, stream: false);
                this.clip.SetData(this.f_decoding.ToArray(), 0);
                this.f_decoding.Clear();
                this.source.clip = this.clip;
                if (this.audioChanged != null)
                {
                    Task.Delay((int)(1000 * missing)).ContinueWith(t => this.audioChanged.Invoke());
                }
                this.source.PlayDelayed(missing);
            }
            // otherwise i can play the audio immediately
            else
            {
                Debug.Log("StreamingPCMDownloadHandler :: CompleteContent - DOWNLOAD COMPLETE!");
                this.clip = AudioClip.Create("Response", this.f_decoding.Count, this.channels, this.sampleRate, stream: false);
                this.clip.SetData(this.f_decoding.ToArray(), 0);
                this.f_decoding.Clear();
                this.source.clip = this.clip;
                if (this.audioChanged != null)
                {
                    this.audioChanged.Invoke();
                }
                this.source.PlayOneShot(this.clip);
            }
        }

    }

    // Called when a Content-Length header is received from the server.

    protected override void ReceiveContentLengthHeader(ulong contentLength)
    {
        Debug.Log(string.Format("StreamingPCMDownloadHandler :: ReceiveContentLength - length {0}", contentLength));
    }

}
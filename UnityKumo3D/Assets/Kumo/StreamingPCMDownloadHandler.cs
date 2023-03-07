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
using System.Threading.Tasks;
public class StreamingPCMDownloadHandler : DownloadHandlerScript {

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
    public StreamingPCMDownloadHandler(): base() {

    }

    // Pre-allocated scripted download handler
    // reuses the supplied byte array to deliver data.
    // Eliminates memory allocation.

    public StreamingPCMDownloadHandler(byte[] buffer): base(buffer) {
    }

    public StreamingPCMDownloadHandler(AudioSource source, int sampleRate = 16000, int channels = 1, UnityEvent audioChanged = null): base() {
        this.sampleRate = sampleRate;
        this.channels = channels;
        this.f_decoding = new List<float>();
        this.source = source;
        this.audioChanged = audioChanged;
    }

    // Required by DownloadHandler base class. Called when you address the 'bytes' property.

    protected override byte[] GetData() { return null; }

    // Called once per frame when data has been received from the network.
    // here i decode the audio and play it using the audio player
    protected override bool ReceiveData(byte[] data, int dataLength) {
        if(data == null || data.Length < 1) {
            Debug.Log("StreamingPCMDownloadHandler :: ReceiveData - received a null/empty buffer");
            return false;
        }
        if (this.oddByteSet)
        {
            byte[] data2 = new byte[dataLength + 1];
            data2[0] = this.oddByte;
            Array.Copy(data, 0, data2, 1, dataLength);
            data = data2;
            dataLength++;
            this.oddByteSet = false;
        }
        // if the data is not a multiple of 2, we have a problem
        for(int i = 0; i < dataLength -1; i += 2)
        {
            int sample = BitConverter.ToInt16(data, i);
            this.f_decoding.Add(sample / 32768.0f);
        }
        // if the data is not a multiple of 2
        if(dataLength % 2 == 1)
        {
            this.oddByte = data[dataLength - 1];
            this.oddByteSet = true;
        }
        if (this.source.isPlaying)
        {
            Debug.Log("StreamingPCMDownloadHandler :: ReceiveData - received " + dataLength + " bytes, but source is playing");
        }else{
            this.clip = AudioClip.Create("Response", this.f_decoding.Count, this.channels, this.sampleRate, stream : false);
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
       
        Debug.Log(string.Format("StreamingPCMDownloadHandler :: ReceiveData - received {0} bytes", dataLength));
        return true;
    }

    // Called when all data has been received from the server and delivered via ReceiveData.
    // I call the audio player to empty the buffer here and play the audio
    protected override void CompleteContent() {
        if (this.f_decoding.Count < 1)
        {
            Debug.Log("StreamingPCMDownloadHandler :: CompleteContent - no data to play");
        }else{
            DateTime time2 = DateTime.Now;
            TimeSpan timeSpan = time2.Subtract(this.timer);
            // missing time to wait before playing the audio
            float missing =  this.clip.length - timeSpan.Seconds;
           
            Debug.Log("StreamingPCMDownloadHandler :: CompleteContent - DOWNLOAD COMPLETE!");
            this.clip = AudioClip.Create("Response", this.f_decoding.Count, this.channels, this.sampleRate,stream : false);
            this.clip.SetData(this.f_decoding.ToArray(), 0);
            this.f_decoding.Clear();
            this.source.clip = this.clip;
            if (this.audioChanged != null)
            {
                Task.Delay((int) (1000*missing)).ContinueWith(t=> this.audioChanged.Invoke());
            }
            this.source.PlayDelayed(missing);
        } 
        
    }

    // Called when a Content-Length header is received from the server.

    protected override void ReceiveContentLengthHeader(ulong contentLength) {
        Debug.Log(string.Format("StreamingPCMDownloadHandler :: ReceiveContentLength - length {0}", contentLength));
    }

}
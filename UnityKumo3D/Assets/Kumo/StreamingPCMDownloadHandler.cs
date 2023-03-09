using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.Networking;
using System;
using System.Threading.Tasks;

/// <summary>
/// Class <c>StreamingPCMDownloadHandler</c> Download handler that decodes PCM data from a server response. It immediately plays the audio as it is received. 
/// To avoid lag, a pause is detected whenever the audio is silent for a certain amount of time (pauseLength). The audio is played only when a chunk before a pause is completely received.
/// The audioClip is updated in real time, and if played back again at the end of the transmission, it won't contain the whole audio.
/// </summary> 
public class StreamingPCMDownloadHandler : DownloadHandlerScript
{
    #region Public Properties
    /// <summary>
    /// <c>AudioClip </c> that is played
    /// </summary>
    public AudioClip clip;
    /// <summary>
    /// <c>AudioSource </c> audio source that plays the audio clip
    /// </summary>
    public AudioSource source;
    #endregion
    #region Private Properties
    /// <summary>
    /// <c>int </c> sample rate of the audio in the clip
    /// </summary>
    private int sampleRate;
    /// <summary>
    /// <c>int </c> number of channels in the clip
    /// </summary>
    private int channels;
    /// <summary>
    /// <c>List<float> </c> list of float that contains a temporary buffer of the audio data to prevent lag
    /// </summary>
    private List<float> f_decoding;
    /// <summary>
    /// <c> DateTime </c> timer to measure the time between two calls of the ReceiveData function to play delayed audio
    private DateTime timer;
    /// <summary>
    /// <c> bool </c> flag to indicate if the chunk of data is odd. This is used to fix the edge case when the data is not a multiple of 2 for the decoding
    /// </summary>
    private bool oddByteSet = false;
    /// <summary>
    /// <c> byte </c> to store the odd byte. This is used to fix the edge case when the data is not a multiple of 2 for the decoding
    /// </summary>
    private byte oddByte;
    /// <summary>
    /// <c> UnityEvent </c> event to trigger when the audioClip is updated with new audio replacing the existing audio
    /// </summary>
    private UnityEvent audioChanged;
    /// <summary>
    /// <c> int </c> number of 0 in the audio stream to detect a pause. Used to prevent lag
    /// </summary>
    private int pauseLength = 100;
    #endregion

    /// <summary>
    /// <c>StreamingPCMDownloadHandler</c> constructor
    /// </summary>
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
        (skip, dataLength) = this.OddByteFix(data, dataLength);
        int pause = this.PauseDetector(data, skip, dataLength);
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
            // save the remaining data for the next call
            for (int i = pause; i < dataLength; i += 2)
            {
                int sample = BitConverter.ToInt16(data, i);
                this.f_decoding.Add(sample / 32768.0f);
            }

        }

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
            if (this.clip != null && this.source.isPlaying)
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

    /// <summary>
    /// Method <c>PauseDetector</c> function to detect if a pause is detected in the audio, and stop the playing if the data is not received
    /// The pause is coded by a number of 0 in the audio stream
    /// param <c>byte[] data</c> the audio data
    /// param <c>int skip</c> the number of bytes to skip at the beginning of the data
    /// param <c>int length</c> the number of bytes to read in the data
    /// return <c>int</c> the position of the pause in the data
    /// </summary>
    private int PauseDetector(byte[] data, int skip, int length)
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
    /// <summary>
    /// Method <>OddByteFix</> function to fix the very edge case when the data is not a multiple of 2. 
    /// Saved the last byte from the previous call and prepend it to the data.
    /// param <c>byte[] data</c> the audio data
    /// param <c>int length</c> the number of bytes to read in the data
    /// return <c>(int,int)</c> start position and length of the data to read for the next call ( may increase or decrease the length of the data by 1 byte)
    private (int, int) OddByteFix(byte[] data, int length)
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
        if ((length - skip) % 2 == 1)
        {
            this.oddByte = data[length - 1];
            this.oddByteSet = true;
            length -= 1;
        }

        return (skip, length);
    }
}
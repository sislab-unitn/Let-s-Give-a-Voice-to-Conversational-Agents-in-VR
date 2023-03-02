using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;
using System.IO;
using System;
using System.Globalization;
using System.Text;
public static class Audio
{
    public static float getAudioLevel(AudioClip clip, int position, double seconds)
    {
        float[] data = new float[clip.samples * clip.channels];
        clip.GetData(data, 0);
        int start = (int)(position - seconds * clip.frequency*clip.channels);
        start = start < 0 ? 0 : start;
        int end = (int)(position);
        // Debug.Log("start: " + start + " end: " + end);
        float sum = 0;
        for (int i = start; i < end; i++)
        {
            sum += Mathf.Abs(data[i]);
        }
        return sum / (end - start);
    }
    // trims the audio clip to the given position from the beginning
    public static AudioClip trimAudioClip(AudioClip clip, int position)
    {

        var soundData = new float[clip.samples * clip.channels];
        clip.GetData(soundData, 0);
        var newData = new float[position * clip.channels];
        for (int i = 0; i < newData.Length; i++)
        {
            newData[i] = soundData[i];
        }
        AudioClip newClip = AudioClip.Create(clip.name, position, clip.channels, clip.frequency, stream: false);
        newClip.SetData(newData, 0);
        return newClip;
    
    }
    // trim audio clip from two positions
    public static AudioClip trimAudioClip(AudioClip clip, int startPosition, int endPosition)
    {
        var soundData = new float[clip.samples * clip.channels];
        clip.GetData(soundData, 0);
        var newData = new float[(endPosition - startPosition) * clip.channels];
        for (int i = 0; i < newData.Length; i++)
        {
            newData[i] = soundData[i + startPosition * clip.channels];
        }
        AudioClip newClip = AudioClip.Create(clip.name, endPosition - startPosition, clip.channels, clip.frequency, stream: false);
        newClip.SetData(newData, 0);
        return newClip;
    }
    // from soundwav module
    public static byte[] ConvertWav(AudioClip clip)
    {
        // wav file header size
        const int HEADER_SIZE = 44;
        byte[] arr = new byte[44];

        float[] clipData = new float[clip.samples];
        int frequency = clip.frequency;
        int numOfChannels = clip.channels;
        int samples = clip.samples;
        //Header

        // Chunk ID
        byte[] riff = Encoding.ASCII.GetBytes("RIFF");
        Array.Copy(riff, 0, arr, 0, 4);
        // ChunkSize
        byte[] chunkSize = BitConverter.GetBytes((HEADER_SIZE + clipData.Length) - 8);
        Array.Copy(chunkSize, 0, arr, 4, 4);
        // Format
        byte[] wave = Encoding.ASCII.GetBytes("WAVE");
        Array.Copy(wave, 0, arr, 8, 4);
        // Subchunk1ID
        byte[] fmt = Encoding.ASCII.GetBytes("fmt ");
        Array.Copy(fmt, 0, arr, 12, 4);
        // Subchunk1Size
        byte[] subChunk1 = BitConverter.GetBytes(16);
        Array.Copy(subChunk1, 0, arr, 16, 4);
        // AudioFormat
        byte[] audioFormat = BitConverter.GetBytes(1);
        Array.Copy(audioFormat, 0, arr, 20, 2);
        // NumChannels
        byte[] numChannels = BitConverter.GetBytes(numOfChannels);
        Array.Copy(numChannels, 0, arr, 22, 2);
        // SampleRate
        byte[] sampleRate = BitConverter.GetBytes(frequency);
        Array.Copy(sampleRate, 0, arr, 24, 4);
        // ByteRate
        byte[] byteRate = BitConverter.GetBytes(frequency * numOfChannels * 2); // sampleRate * bytesPerSample*number of channels, here 44100*2*2
        Array.Copy(byteRate, 0, arr, 28, 4);
        // BlockAlign
        ushort blockAlign = (ushort)(numOfChannels * 2);
        Array.Copy(BitConverter.GetBytes(blockAlign), 0, arr, 32, 2);
        // BitsPerSample
        ushort bps = 16;
        byte[] bitsPerSample = BitConverter.GetBytes(bps);
        Array.Copy(bitsPerSample, 0, arr, 34, 2);
        // Subchunk2ID
        byte[] datastring = Encoding.ASCII.GetBytes("data");
        Array.Copy(datastring, 0, arr, 36, 4);
        // Subchunk2Size
        byte[] subChunk2 = BitConverter.GetBytes(samples * numOfChannels * 2);
        Array.Copy(subChunk2, 0, arr, 40, 4);
        // Data

        clip.GetData(clipData, 0);
        short[] intData = new short[clipData.Length];
        byte[] bytesData = new byte[clipData.Length * 2];

        int convertionFactor = 32767;

        for (int i = 0; i < clipData.Length; i++)
        {
            intData[i] = (short)(clipData[i] * convertionFactor);
            byte[] byteArr = new byte[2];
            byteArr = BitConverter.GetBytes(intData[i]);
            byteArr.CopyTo(bytesData, i * 2);
        }
        // concatenate header and data
        byte[] final = new byte[arr.Length + bytesData.Length];
        arr.CopyTo(final, 0);
        bytesData.CopyTo(final, arr.Length);
        return final;
    }
}
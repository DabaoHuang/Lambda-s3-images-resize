# Lambda-s3-images-resize

<!-- English | [繁體中文](./README.zh-TW.md) -->

<p align="center">
  <a href="#">
    <img src="./logo.png">
  </a>
</p>

![Language](https://img.shields.io/badge/python-3.6-blue)
![Size](https://img.shields.io/badge/size-5.5MB-lightgrey)
[![GitHub license](https://img.shields.io/github/license/Naereen/StrapDown.js.svg)](https://github.com/Naereen/StrapDown.js/blob/master/LICENSE)

## How to use?
```
$ zip -r code.zip
```
Upload to AWS Lambda function

## Environment variables
![Environment variables](./Environment.jpg)
 - SIZECHART - Split with ','. ex: 300x300,100x100...
 - SOURCE_BUCKET - Your source image s3 bucket.
 - SOURCE_PREFIX - Your source prefix path.
 - TARGET_BUCKET - Your target s3 bucket.
 - TARGET_PREFIX - Your target prefix path.

## Execution role
Must be attach a ROLE from below policy to AWS Lambda function.
```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
          "s3:PutObject",
          "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::__YOUR_BUCKET_NAME_HERE__/*"    
    }
  ]
}
```
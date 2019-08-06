from PIL import Image
from io import BytesIO
import boto3, botocore, os, re, base64

s3 = boto3.resource('s3')

# Lambda Environment Variables
source_bucket     = os.environ['SOURCE_BUCKET']
source_prefix_key = os.environ['SOURCE_PREFIX']
target_bucket     = os.environ['TARGET_BUCKET']
target_prefix_key = os.environ['TARGET_PREFIX']
sizechart         = os.environ['SIZECHART']

def check_object_exists(bucket, key):
    try:
        s3.Object(bucket, key).load()
    except botocore.exceptions.ClientError as e:
        return False
    else:
        return True

def lambda_handler(event, context):

    # s3 307 answer
    try:
        key = event['queryStringParameters']['key']
    except NameError as e:
        return {
            "statucCode" : "404",
            "body" : "Can not find the key."
        }
    print("key: "+key)
    match = re.search('((\d+)[a-zA-Z](\d+))\/(.*)',key)
    
    # check in size chart
    if match.group(1) not in sizechart.split(',') :
        print("size chart: "+match.group(1))
        return {
            'statusCode' : '404',
            'body' : 'Sizechart not found.'
        }

    width = int(match.group(2))
    height = int(match.group(3))
    extension = os.path.splitext(key)[1].lower()
    key = str(match.group(4))
    # path: prefix/WxH/W_H_key
    putkey = target_prefix_key + str(width) + "x" + str(height) + "/" + str(width) + '_' + str(height) + '_' + key
    key = source_prefix_key + key

    if extension in ['.jpeg', '.jpg']:
        format = 'JPEG'
    if extension in ['.png']:
        format = 'PNG'
    
    # check object exists
    if check_object_exists(target_bucket, putkey) == False :
        
        if check_object_exists(source_bucket, key) == False :
            return {
                'statusCode' : '404',
                'body' : 'Image name not found.'
            }

        # get original's images
        obj = s3.Object(
            bucket_name=source_bucket,
            key=key
        )

        obj_body = obj.get()['Body'].read()

        img = Image.open(BytesIO(obj_body))
        SourceWidth , SourceHeight = img.size

        # Make image to not distortion
        # Based on width
        if SourceWidth >= SourceHeight :
            if SourceWidth > width :
                # width:x = SourceWidth:SourceHeight
                ResizeWidth = width
                ResizeHeight = int(width*SourceHeight/SourceWidth)
        # Based on height
        else :
            if SourceHeight >= height :
                # x:height = SourceWidth:SourceHeight
                ResizeHeight = height
                ResizeWidth = int(height*SourceWidth/SourceHeight)

        if 'ResizeWidth' not in locals() and 'ResizeHeight' not in locals() :
            ResizeWidth = SourceWidth
            ResizeHeight = SourceHeight
            
        img = img.resize( (ResizeWidth, ResizeHeight) , Image.ANTIALIAS )

        # Past white background
        ResultImage = Image.new("RGB", [width,height],(255,255,255,255))
        ResultImage.paste(img,(int((width - img.size[0]) / 2), int((height - img.size[1]) / 2)))

        # distortion
        # img = img.resize((width, height), PIL.Image.ANTIALIAS)
        buffer = BytesIO()
        ResultImage.save(buffer,format)
        buffer.seek(0)

        obj = s3.Object(
            bucket_name=target_bucket,
            key=putkey
            #content_type='image/'+str(format).lower()
        )
        obj.put(Body=buffer)
        #obj.Acl(ACL='public-read')
        hex_data = buffer.getvalue()
    
    else:
        obj = s3.Object(
            bucket_name=target_bucket,
            key=putkey
            # content_type='image/'+str(format).lower()
        )
        hex_data = obj.get()['Body'].read()

    # print(base64.b64encode(hex_data).decode("utf-8"))

    return {
        "isBase64Encoded": True,
        "statusCode": 200,
        "headers": { "content-type": "image/jpg"},
        "body":  base64.b64encode(hex_data).decode("utf-8")
        }
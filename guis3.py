#!/bin/python3
# S3 upload tool
# By:kaer TG:@seedccy

import boto3, yaml, os
from loguru import logger
from gooey import Gooey, GooeyParser


# Configs()配置文件位置
def Configs():
    try:
        # 编译后config.yaml 必须在此路径：/Applications/guis3.app/Contents/MacOS/config.yaml ，app名字不可更改
        conf = '/Applications/guis3.app/Contents/MacOS/config.yaml'
        if os.path.isfile(conf):
            print(conf)
            return conf
        else:
            write_yaml('Your-AKI', 'Your-SAK', 'Region-where-S3-is-located', 'S3-bucket-name')
            return conf
    except Exception as e:
        conf = os.path.abspath('/Applications/guis3.app/Contents/MacOS/config.yaml')
        print(conf)
        return conf

# write_yaml() 保存yaml
def write_yaml(CN_S3_AKI, CN_S3_SAK, CN_REGION_NAME, BUCKET_NAME):
    data = dict(S3=dict(
        S3_AKI=CN_S3_AKI,
        S3_SAK=CN_S3_SAK,
        REGION_NAME=CN_REGION_NAME,
        BUCKET_NAME=BUCKET_NAME, )
    )
    with open('/Applications/guis3.app/Contents/MacOS/config.yaml', encoding="utf-8", mode="w") as f:
        yaml.dump(data, f, default_flow_style=False)
        print("存储yaml成功")

# 覆盖上传
def upload_files(path_local, path_s3):
    """
    上传（重复上传会覆盖同名文件）
    :param path_local: 本地路径
    :param path_s3: s3路径
    """
    logger.info(f'Start upload files.')

    if not upload_single_file(path_local, path_s3):
        logger.error(f'Upload files failed.')

    logger.info(f'Upload files successful.')

# 单文件上传
def upload_single_file(src_local_path, dest_s3_path):
    """
    上传单个文件
    :param src_local_path:
    :param dest_s3_path:
    :return:
    """
    try:
        with open(src_local_path, 'rb') as f:
            s3.upload_fileobj(f, BUCKET_NAME, dest_s3_path)
    except Exception as e:
        logger.error(f'Upload data failed. | src: {src_local_path} | dest: {dest_s3_path} | Exception: {e}')
        return False
    logger.info(f'Uploading file successful. | src: {src_local_path} | dest: {dest_s3_path}')
    return True


if __name__ == "__main__":
    with open(Configs(), 'r') as f:
        config = yaml.safe_load(f)
    CN_S3_AKI = config['S3']['S3_AKI']
    CN_S3_SAK = config['S3']['S3_SAK']
    CN_REGION_NAME = config['S3']['REGION_NAME']
    BUCKET_NAME = config['S3']['BUCKET_NAME']
    # s3 实例
    s3 = boto3.client('s3', region_name=CN_REGION_NAME,
                      aws_access_key_id=CN_S3_AKI, aws_secret_access_key=CN_S3_SAK
                      )


    desc = "工具阐明:" + "\n" + "   " + "AWS S3上传工具"


    @Gooey(
        show_config=True,
        # richtext_controls=True,
        language='chinese',
        header_show_title=False,
        program_name="AWS S3上传工具",
        body_bg_color="#999900",
        footer_bg_color="#999900",
        header_bg_color="#999900",
        terminal_panel_color="#999900",
        terminal_font_color="#99FF00",
        encoding="utf-8",
        default_size=(700, 500),
        progress_expr="current / total * 100",

        # 再次执行，革除之前执行的日志
        clear_before_run=True,
        timing_options={'show_time_remaining': True, 'hide_time_remaining_on_complete': False}  # 设置编码格式，打包的时候遇到问题
    )
    def main():
        parser = GooeyParser(description=desc)
        return parser
    parser = main()
    parser.add_argument(option_strings=['-u', '--up'], dest='选择上传文件夹', widget="DirChooser")
    parser.add_argument(option_strings=['-d', '--dir'], help='设置S3上传后的路径，默认为根目录,自定义目录写法:test/', dest='上传至S3路径', widget="TextField", type=str, default='/')
    parser.add_argument(option_strings=['-a', '--aki'], help='用户AKI，开始后配置自动保存', dest='CN_S3_AKI', widget="TextField", type=str, default=CN_S3_AKI)
    parser.add_argument(option_strings=['-s', '--sak'], help='用户SAK，开始后配置自动保存', dest='CN_S3_SAK', widget="TextField", type=str, default=CN_S3_SAK)
    parser.add_argument(option_strings=['-r', '--rn'], help='aws s3桶所在区域如:ap-east-1 开始后配置自动保存', dest='REGION_NAME', widget="TextField", type=str, default=CN_REGION_NAME)
    parser.add_argument(option_strings=['-b', '--bn'], help='s3桶名称 开始后配置自动保存', dest='BUCKET_NAME', widget="TextField", type=str, default=BUCKET_NAME)

    # 获取参数
    args = vars(parser.parse_args())
    # 根据指定key 获取数据
    print("你选择的文件夹：", args['选择上传文件夹'], flush=True)

    # #写入yam 顺序：CN_S3_AKI, CN_S3_SAK, CN_REGION_NAME, BUCKET_NAME
    write_yaml(args['CN_S3_AKI'], args['CN_S3_SAK'], args['REGION_NAME'], args['BUCKET_NAME'])
    s3 = boto3.client('s3', region_name=args['REGION_NAME'],
                      aws_access_key_id=args['CN_S3_AKI'], aws_secret_access_key=args['CN_S3_SAK']
                      )
    BUCKET_NAME = args['BUCKET_NAME']
    # 上传字符串操作
    for file in os.listdir(args['选择上传文件夹']):
        files = str(args['选择上传文件夹']) + '/' + file
        print(files, flush=True)
        if args['上传至S3路径'] == '/':
            path_s3 = file
            upload_files(files, path_s3)
        else:
            path_s3 = str(args['上传至S3路径']) + file
            upload_files(files, path_s3)

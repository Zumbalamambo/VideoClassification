from TFFusions.all_video_models.moe_model import MoeModel
from TFFusions.all_video_models.chain_moe_model import ChainMoeModel
from TFFusions.all_video_models.logistic_model import LogisticModel
from TFFusions.all_video_models.full_connect_model import FullConnectModel

def GetVideoModel(video_model_name):
    if video_model_name == 'moe_model':
        return MoeModel
    elif video_model_name == 'chain_moe_model':
        return ChainMoeModel
    elif video_model_name == 'LogisticModel':
        return LogisticModel
    elif video_model_name == 'FullConnectModel':
        return FullConnectModel
    else:
        raise NotImplementedError

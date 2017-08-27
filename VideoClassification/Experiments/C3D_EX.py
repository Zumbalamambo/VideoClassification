import torch
import torch.nn as nn

try:
    from cv2 import cv2
except:
    import cv2

import VideoClassification.Config.Config as Config
from VideoClassification.model.C3D.C3D import C3D
from VideoClassification.utils.Others.Logger import Logger
from VideoClassification.utils.DataSetLoader.UCF101_DataSetLoader_FromFileName.UCF101Loader import test_UCF101_C3D, \
    train_UCF101_C3D
from VideoClassification.utils.Others.toolkits import accuracy, try_to_load_state_dict
from VideoClassification.utils.DataSetLoader.UCF101_DataSetLoader_FromFileName.PictureQueue import PictureQueue, \
    GenVariables_C3D

'''
C3D
'''

############ Config

logger = Logger(Config.LOGSpace + Config.EX_ID)
savepath = Config.ExWorkSpace + Config.EX_ID + '/'

import os.path

if os.path.isdir(savepath) == False:
    os.mkdir(savepath)

batchsize = 22


############


def C3D_Net_Run():
    epochs = 81
    loops = 2001
    learningrate = 0.0001
    attenuation = 0.1

    model = C3D(drop=0.9).cuda()

    if Config.LOAD_SAVED_MODE_PATH is not None:
        import types
        model.try_to_load_state_dict = types.MethodType(try_to_load_state_dict, model)
        model.try_to_load_state_dict(torch.load(Config.LOAD_SAVED_MODE_PATH))
        print('LOAD {} done!'.format(Config.LOAD_SAVED_MODE_PATH))

    lossfunc = nn.CrossEntropyLoss()
    optim = torch.optim.Adam(model.parameters(), lr=learningrate)

    pq_train = PictureQueue(dsl=train_UCF101_C3D(), Gen=GenVariables_C3D, batchsize=batchsize, worker=5)
    pq_test = PictureQueue(dsl=test_UCF101_C3D(), Gen=GenVariables_C3D, batchsize=batchsize, worker=2)

    cnt = 0
    for epoch in range(epochs):

        for l in range(loops):

            cnt += 1

            imgs, labels = pq_train.Get()

            model.zero_grad()
            pred = model(imgs)

            loss = lossfunc(pred, labels)

            logger.scalar_summary('C3D/train_loss', loss.data[0], cnt)

            loss.backward()

            optim.step()

            print('C3D epoch: {} cnt: {} loss: {}'.format(epoch, cnt, loss.data[0]))

            if cnt % 25 == 0:
                imgs, labels = pq_test.Get()
                pred = model.inference(imgs)
                loss = lossfunc(pred, labels)

                logger.scalar_summary('C3D/test_loss', loss.data[0], cnt)

                # acc
                acc = accuracy(pred, labels, topk=(1, 5, 10))
                logger.scalar_summary('C3D/test_acc@1', acc[0], cnt)
                logger.scalar_summary('C3D/test_acc@5', acc[1], cnt)
                logger.scalar_summary('C3D/test_acc@10', acc[2], cnt)

                imgs, labels = pq_train.Get()
                pred = model.inference(imgs)

                acc = accuracy(pred, labels, topk=(1, 5, 10))
                logger.scalar_summary('C3D/train_acc@1', acc[0], cnt)
                logger.scalar_summary('C3D/train_acc@5', acc[1], cnt)
                logger.scalar_summary('C3D/train_acc@10', acc[2], cnt)

            if cnt % 2000 == 0:
                savefile = savepath + 'C3D_EX1_{:02d}.pt'.format(epoch % 20)
                print('C3D save model to {}'.format(savefile))
                torch.save(model.state_dict(), savefile)

        if epoch in [20, 40, 60]:
            learningrate = learningrate * attenuation
            optim = torch.optim.Adam(model.parameters(), lr=learningrate)


if __name__ == '__main__':
    # C3D_Net_Run()
    pass

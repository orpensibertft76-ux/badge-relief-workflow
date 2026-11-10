"""Prepare a smooth floating-point relief height field without changing any scene."""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import median_filter, gaussian_filter

def sample_bilinear(field,u,v):
    h,w=field.shape
    x=np.clip(np.asarray(u,dtype=float),0,1)*(w-1)
    y=np.clip(np.asarray(v,dtype=float),0,1)*(h-1)
    a=np.floor(x).astype(int); b=np.floor(y).astype(int)
    aa=np.minimum(a+1,w-1); bb=np.minimum(b+1,h-1)
    dx=x-a; dy=y-b
    return ((1-dx)*(1-dy)*field[b,a]+dx*(1-dy)*field[b,aa]
            +(1-dx)*dy*field[bb,a]+dx*dy*field[bb,aa])

def prepare(path,median_size=3,sigma_px=1.6):
    with Image.open(path) as im:
        if 'A' in im.getbands() and im.getchannel('A').getextrema()[0]<255:
            raise ValueError('Explicitly composite transparent input onto a chosen background first.')
        if im.mode in ('I;16','I;16L','I;16B','I'):
            g=np.asarray(im,dtype=np.float32)
            if g.min()<0 or g.max()>65535: raise ValueError('Expected unsigned 16-bit heights.')
            g=g/65535.
        elif im.mode=='F':
            g=np.asarray(im,dtype=np.float32)
            if not np.isfinite(g).all() or g.min()<0 or g.max()>1:
                raise ValueError('Expected finite normalized float heights.')
        else:
            g=np.asarray(im.convert('L'),dtype=np.float32)/255.
    return gaussian_filter(median_filter(g,size=median_size,mode='reflect'),sigma=sigma_px,mode='reflect')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',required=True,type=Path)
    p.add_argument('--out-dir',required=True,type=Path)
    p.add_argument('--width-mm',type=float,required=True)
    p.add_argument('--sigma-px',type=float,default=1.6)
    p.add_argument('--median-size',type=int,default=3)
    a=p.parse_args()
    if a.width_mm<=0 or a.sigma_px<0 or a.median_size<1 or a.median_size%2==0:
        p.error('Positive width, nonnegative sigma, positive odd median size required.')
    targets=[a.out_dir/n for n in ('height.npy','height_16bit.png','parameters.json')]
    if any(t.exists() for t in targets): raise FileExistsError('Choose a new output version directory.')
    g=prepare(a.input,a.median_size,a.sigma_px)
    a.out_dir.mkdir(parents=True,exist_ok=True)
    np.save(targets[0],g)
    Image.fromarray(np.round(np.clip(g,0,1)*65535).astype(np.uint16)).save(targets[1])
    params={'source':str(a.input.resolve()),'shape':list(g.shape),'median_size':a.median_size,
            'sigma_px':a.sigma_px,'width_mm':a.width_mm,'sigma_mm_x':a.sigma_px*a.width_mm/g.shape[1],
            'mapping':'z=base_mm+relief_mm*height; no automatic contrast stretch',
            'coordinates':'image rows top to bottom; v=0 at top'}
    targets[2].write_text(json.dumps(params,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(params,ensure_ascii=False))

if __name__=='__main__': main()

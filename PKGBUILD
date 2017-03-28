# Maintainer: 0xFelix

pkgname=python-viessmann-tools
pkgver=0.5
pkgrel=1
pkgdesc='Monitor and reset Viessmann heaters'
arch=(any)
license=(GPLv3)
depends=(python vcontrold)
source=('setup.py'
        'viessmanntools.py'
	'viessmanntools.conf'
        'vclient-to-mqtt'
        'vclient-to-mqtt.service'
	'vito-reset'
	'vito-reset.service')
sha256sums=('e5d57bfa3d2aecf33f8f1f94fa1e607cfff71e05b8932cf617ca8158a1a5991c'
            'cbcf7b69afa57900635ae9d81213fb76a66948136620e9dabe9590ec7ff20a64'
	    '80f9146b7b95ae768d89ef3ea0faf27c1ef221d90586f516868dc0454e3e16f6'
	    '7b85716995d1ef5f0b923f8dc35d4dc2ab4b5f089a44ddca3f66ecb673f1a9e4'
	    '0a1f6e8964de8b71bfe46b1e58ba4fc99da008d1f20977002667ac288950b28f'
	    'cece71ba3020831fa58c3d6436cb61acf67d561eb7a25eb117635dea576e06c6'
	    'aed1567f49f82b3de8cc07efe8d2d3ca8748e0f438ba60aa4fbbfdb68bfdf74d')

package() {
  python setup.py install --root="$pkgdir/" --optimize=1

  install -Dm 644 "${srcdir}/viessmanntools.conf" "${pkgdir}/etc/viessmanntools.conf"

  install -Dm 755 "${srcdir}/vclient-to-mqtt" "${pkgdir}/usr/bin/vclient-to-mqtt" 
  install -Dm 644 "${srcdir}/vclient-to-mqtt.service" "${pkgdir}/usr/lib/systemd/system/vclient-to-mqtt.service"
  
  install -Dm 755 "${srcdir}/vito-reset" "${pkgdir}/usr/bin/vito-reset" 
  install -Dm 644 "${srcdir}/vito-reset.service" "${pkgdir}/usr/lib/systemd/system/vito-reset.service"
}

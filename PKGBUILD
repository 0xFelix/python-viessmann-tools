# Maintainer: 0xFelix

pkgname=python-viessmann-tools
pkgver=0.3
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
sha256sums=('42416d96de7e752004e1615fb6ef93c7889933c8c323b56ae95d3de8b7e3123b'
            '46098b447201105b93a22a8587aebd6b7a2ddffa03e5b3c015970027855080e0'
	    'bec6392b11d09e60cbf7b6076d4f61f2bc2e85fd8869efa7f35de5b85956a5c4'
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

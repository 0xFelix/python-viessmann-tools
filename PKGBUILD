# Maintainer: 0xFelix

pkgname=python-viessmann-tools
pkgver=0.6
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
sha256sums=('5c925ddc36abf2b24222d73cfed1a1336e9ba36b0147a42d928c9b2dc4852ff9'
            'cbcf7b69afa57900635ae9d81213fb76a66948136620e9dabe9590ec7ff20a64'
	    '80f9146b7b95ae768d89ef3ea0faf27c1ef221d90586f516868dc0454e3e16f6'
	    '7b85716995d1ef5f0b923f8dc35d4dc2ab4b5f089a44ddca3f66ecb673f1a9e4'
	    'b4c2a2ba24b873c8c064b767ff119eb725e4c99ffbad206d866b24cc3f3410c9'
	    'cece71ba3020831fa58c3d6436cb61acf67d561eb7a25eb117635dea576e06c6'
	    '1fe436ceab3f9b041ba816cdb3bf06d292bcaf98d37c163e84db77f0d1c83caf')

package() {
  python setup.py install --root="$pkgdir/" --optimize=1

  install -Dm 644 "${srcdir}/viessmanntools.conf" "${pkgdir}/etc/viessmanntools.conf"

  install -Dm 755 "${srcdir}/vclient-to-mqtt" "${pkgdir}/usr/bin/vclient-to-mqtt" 
  install -Dm 644 "${srcdir}/vclient-to-mqtt.service" "${pkgdir}/usr/lib/systemd/system/vclient-to-mqtt.service"
  
  install -Dm 755 "${srcdir}/vito-reset" "${pkgdir}/usr/bin/vito-reset" 
  install -Dm 644 "${srcdir}/vito-reset.service" "${pkgdir}/usr/lib/systemd/system/vito-reset.service"
}

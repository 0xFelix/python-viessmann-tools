# Maintainer: 0xFelix

pkgname=python-viessmann-tools
pkgver=0.7
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
sha256sums=('40408187d37c1b16119c682e699b7abde5159a9162f4340b2598e6a5efe807ac'
            '531b8f6594b3c1225c033262112f837164d675b1c3fc44f1b4165e0d05a2d158'
	    '1ef5918ba357c13c3dc91829ada3efcdcdde649f978546685cab4bf3835bab49'
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

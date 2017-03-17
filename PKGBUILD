# Maintainer: 0xFelix

pkgname=python-viessmann-tools
pkgver=0.1
pkgrel=1
pkgdesc='Monitor and reset Viessmann heaters'
arch=(any)
license=(GPLv3)
depends=(python vcontrold)
source=('setup.py'
        'viessmanntools.py'
        'vclient-to-mqtt'
        'vclient-to-mqtt.service'
	'vito-reset'
	'vito-reset.service')
sha256sums=('33e11ae2a31eb9c237ed1745ac4bf5e70751495a1f1f87e389fdc5721418d166'
            '500ace3e2f1aa0135404629331a598dcd749ab6b0a86839cd6ce9622456583bd'
	    '14a81f8d8820754e024487fed9a50d5b639e7f10897301f28f3118ffd0d68277'
	    '0a1f6e8964de8b71bfe46b1e58ba4fc99da008d1f20977002667ac288950b28f'
	    '57f782e742654c6a22feaf158219948b2bb9b4a759abde1b83016ab772def22a'
	    'aed1567f49f82b3de8cc07efe8d2d3ca8748e0f438ba60aa4fbbfdb68bfdf74d')

package() {
  python setup.py install --root="$pkgdir/" --optimize=1

  install -Dm 755 "${srcdir}/vclient-to-mqtt" "${pkgdir}/usr/bin/vclient-to-mqtt" 
  install -Dm 644 "${srcdir}/vclient-to-mqtt.service" "${pkgdir}/usr/lib/systemd/system/vclient-to-mqtt.service"
  
  install -Dm 755 "${srcdir}/vito-reset" "${pkgdir}/usr/bin/vito-reset" 
  install -Dm 644 "${srcdir}/vito-reset.service" "${pkgdir}/usr/lib/systemd/system/vito-reset.service"
}

# Maintainer: 0xFelix

pkgname=python-viessmann-tools
pkgver=0.2
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
sha256sums=('0a6d8836c18d979b9e7daf7b76441fee1b7d9db2bb4beb1ba66cbd756462e404'
            '56357a1765647ff7e68530490515ab69495df6d2d8a88d6021afae3a9e9737d0'
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

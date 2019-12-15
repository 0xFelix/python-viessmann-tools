# Maintainer: 0xFelix

pkgname=python-viessmann-tools
pkgver=0.8.0
pkgrel=1
pkgdesc='Monitor and reset Viessmann heaters'
arch=(armv6h armv7h aarch64)
url='https://github.com/0xFelix/python-viessmann-tools'
license=('GPL3')
depends=(python python-paho-mqtt python-raspberry-gpio vcontrold)
backup=('etc/viessmanntools.conf')
source=("pyvt::git+https://github.com/0xFelix/python-viessmann-tools.git#tag=v$pkgver")
sha256sums=('SKIP')

package() {
  cd "$srcdir/pyvt"
  python setup.py install --prefix=/usr --root="$pkgdir" --optimize=1

  install -Dm 644 "$srcdir/pyvt/viessmanntools.conf" "$pkgdir/etc/viessmanntools.conf"

  install -Dm 755 "$srcdir/pyvt/vclient-to-mqtt" "$pkgdir/usr/bin/vclient-to-mqtt"
  install -Dm 644 "$srcdir/pyvt/vclient-to-mqtt.service" "$pkgdir/usr/lib/systemd/system/vclient-to-mqtt.service"

  install -Dm 755 "$srcdir/pyvt/vito-reset" "$pkgdir/usr/bin/vito-reset"
  install -Dm 644 "$srcdir/pyvt/vito-reset.service" "$pkgdir/usr/lib/systemd/system/vito-reset.service"
}

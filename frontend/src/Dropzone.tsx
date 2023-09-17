import {useDropzone} from 'react-dropzone';
import axios from 'axios';

interface DropzoneProps {
    customMessage?: string;
}


function Dropzone({customMessage}: DropzoneProps) {
    const {getRootProps, getInputProps } = useDropzone({
        onDrop: (acceptedFiles: File[]) => {
            acceptedFiles.forEach((file: File) => {
                const options = {
                    url: 'http://localhost:5000/process',
                    method: 'POST',
                    headers: {
                      'Accept': 'application/json',
                      'Access-Control-Allow-Origin': '*'
                    },
                    data: {
                        path: file.name
                    }
                  };
                  
                axios(options)
                    .then(response => {
                        console.log(response.status);
                });

            });
        }
    });

    const message = customMessage ? customMessage : "Drag 'n' drop some files here, or click to select files";

    return (
        <section className="container">
            <div {...getRootProps({className: 'dropzone'})}>
                <input {...getInputProps()} />
                <p>{message}</p>
            </div>
        </section>
    );
}

export default Dropzone;
